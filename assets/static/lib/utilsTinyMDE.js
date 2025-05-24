let saveTimeout = null;
let currentPostId = null;
let lastKnownUpdateTime = null;
const saveTimeoutLength = 3000;

// API interaction abstraction
const apiRequest = (url, method, data = null) => {
  const options = {
    credentials: "include",
    method: method,
    headers: {
      "Content-Type": "application/json",
    },
  };

  if (data) {
    options.body = JSON.stringify(data);
  }

  return fetch(url, options);
};

export const initializeTinyMDE = () => {
  const editorHostElement = document.getElementById("editor");
  const commandBarHostElement = document.getElementById("tinymde-commandbar");

  // Check URL for post ID
  const urlParams = new URLSearchParams(window.location.search);
  currentPostId = urlParams.get("id");

  if (editorHostElement && window.TinyMDE) {
    const editor = setupEditor(editorHostElement);

    if (commandBarHostElement) {
      setupCommandBar(commandBarHostElement, editor);
    }

    // If we have a post ID, load the post content
    if (currentPostId) {
      loadPost(currentPostId, editor);
    }

    // Set up image drop handling
    setupImageDropHandling(editor);
  }
};

const setupEditor = (editorHostElement) => {
  const editor = new window.TinyMDE.Editor({ element: editorHostElement });
  const titleInput = document.getElementById("post-title");

  editor.addEventListener("change", function () {
    if (saveTimeout) {
      clearTimeout(saveTimeout);
    }

    saveTimeout = setTimeout(() => {
      const title = titleInput ? titleInput.value : "";
      savePost(editor.getContent(), title, currentPostId);
    }, saveTimeoutLength);
  });

  if (titleInput) {
    titleInput.addEventListener("input", function () {
      if (saveTimeout) {
        clearTimeout(saveTimeout);
      }

      saveTimeout = setTimeout(() => {
        savePost(editor.getContent(), title, currentPostId);
      }, saveTimeoutLength);
    });
  }

  return editor;
};

const setupCommandBar = (commandBarHostElement, editor) => {
  return new window.TinyMDE.CommandBar({
    element: commandBarHostElement,
    editor: editor,
    commands: [
      "bold",
      "italic",
      "strikethrough",
      "|",
      "code",
      "|",
      "h1",
      "h2",
      "|",
      "ul",
      "ol",
      "|",
      "blockquote",
      "hr",
      "|",
      "insertLink",
      "insertImage",
      "|",
      {
        name: "publish",
        title: "Publish Post",
        innerHTML: `<svg height="18" width="18"><path d="M5 3v10h8V3H5zm1 1h6v8H6V4zm1 2h4v1H7V6zm0 2h4v1H7V8zm0 2h3v1H7v-1z" fill="currentColor"/></svg>`,
        action: function () {
          console.log("Publishing...");
          const title = document.getElementById("post-title").value;
          const content = editor.getContent();

          // Save with the published flag directly in one request
          const method = currentPostId ? "PATCH" : "POST";
          const url = currentPostId
            ? `/api/v1/post/${currentPostId}`
            : "/api/v1/post/";

          apiRequest(url, method, {
            title: title,
            markdown_content: content,
            published: true,
            updated_on: lastKnownUpdateTime,
          });
        },
        hotkey: "Mod-Shift-P",
      },
    ],
  });
};

const loadPost = (postId, editor) => {
  apiRequest(`/api/v1/post/${postId}`, "GET")
    .then((response) => response.json())
    .then((data) => {
      const titleInput = document.getElementById("post-title");
      if (titleInput && data.title) {
        titleInput.value = data.title;
      }

      if (data.markdown_content && editor) {
        editor.setContent(data.markdown_content);
      }
      lastKnownUpdateTime = data.updated_on;
      updatePublishedAndModified(data?.published, data?.updated_on);
    })
    .catch((error) => {
      updateStatusMessage("Error loading post");
    });
};

const publishPost = (postID) => {
  if (!postID) {
    updateStatusMessage("No postID provided");
    return;
  }
  const method = "PATCH";
  const url = `/api/v1/post/${postID}`;
  const postData = {
    published: true,
  };

  apiRequest(url, method, postData);
};
const savePost = (content, title, postID = null) => {
  if (!title) {
    updateStatusMessage("Title required");
    return;
  }

  updateStatusMessage("Saving...");

  const method = postID ? "PATCH" : "POST";
  const url = postID ? `/api/v1/post/${postID}` : "/api/v1/post/";

  const postData = {
    title: title,
    markdown_content: content,
    updated_on: lastKnownUpdateTime,
  };

  apiRequest(url, method, postData)
    .then((response) => {
      if (response.status === 409) {
        // Conflict detected
        updateStatusMessage(
          "Post was modified elsewhere. Reload to see changes.",
        );
        return Promise.reject("Conflict");
      }
      return response.json();
    })
    .then((data) => {
      if (!postID && data.id) {
        currentPostId = data.id;
        const newUrl = new URL(window.location);
        newUrl.searchParams.set("id", data.id);
        window.history.pushState({}, "", newUrl);
      }

      lastKnownUpdateTime = data.updated_on;
      updateStatusMessage("Saved");
      updatePublishedAndModified(data?.published, data?.updated_on);
    })
    .catch((error) => {
      if (error !== "Conflict") {
        updateStatusMessage("Save failed");
      }
    });
};

const updateStatusMessage = (message) => {
  const statusMessage = document.getElementById("status-message");

  if (statusMessage) {
    statusMessage.textContent = message;

    // Clear status after 3 seconds
    setTimeout(() => {
      statusMessage.textContent = "";
    }, 3000);
  }
};

const updatePublishedAndModified = (published, lastModifiedAt) => {
  const statusPublished = document.getElementById("status-published");
  const statusLastModified = document.getElementById("status-last-modified");
  statusPublished.innerText = published ? "Published" : "Draft";
  statusLastModified.innerText = lastModifiedAt ? lastModifiedAt : "";
  return;
};

const setupImageDropHandling = (editor) => {
  editor.addEventListener("drop", function (event) {
    // Check if there are files in the drop
    if (
      event.dataTransfer &&
      event.dataTransfer.files &&
      event.dataTransfer.files.length > 0
    ) {
      const files = event.dataTransfer.files;

      // Check if any of the files are images
      for (let i = 0; i < files.length; i++) {
        const file = files[i];
        if (file.type.startsWith("image/")) {
          uploadAndInsertImage(file, editor);
        }
      }
    }
  });
};

const uploadAndInsertImage = (file, editor) => {
  updateStatusMessage("Uploading image...");

  const formData = new FormData();
  formData.append("image", file);

  fetch("/api/v1/upload", {
    method: "POST",
    credentials: "include",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.path) {
        // Insert markdown image at cursor position
        const imageName = file.name.split(".")[0]; // Use filename as alt text
        const markdownImage = `![${imageName}](${data.path})`;

        // Get current selection and insert the markdown
        const selection = editor.getSelection();
        if (selection) {
          editor.paste(markdownImage, selection, selection);
          updateStatusMessage("Image uploaded");
        }
      } else {
        updateStatusMessage(
          "Upload failed: " + (data.error || "Unknown error"),
        );
      }
    })
    .catch((error) => {
      console.error("Upload error:", error);
      updateStatusMessage("Upload failed");
    });
};
