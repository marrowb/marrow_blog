let saveTimeout = null;
let currentPostId = null;
let lastKnownUpdateTime = null;
let currentPostPublished = false;
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

  const urlParams = new URLSearchParams(window.location.search);
  currentPostId = urlParams.get("id");

  if (!currentPostId) {
    const pathParts = window.location.pathname.split("/");
    const postIndex = pathParts.indexOf("post");
    if (postIndex !== -1 && pathParts[postIndex + 1]) {
      currentPostId = pathParts[postIndex + 1];
    }
  }

  if (editorHostElement && window.TinyMDE) {
    const editor = setupEditor(editorHostElement);

    if (commandBarHostElement) {
      setupCommandBar(commandBarHostElement, editor);
    }

    if (currentPostId) {
      loadPost(currentPostId, editor);
    }

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
  const commandBar = new window.TinyMDE.CommandBar({
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
        name: "preview",
        title: "Preview Post",
        innerHTML: `<svg height="18" width="18"><path d="M9 2C5 2 1 5 1 9s4 7 8 7 8-3 8-7-4-7-8-7zm0 12c-2.8 0-5-2.2-5-5s2.2-5 5-5 5 2.2 5 5-2.2 5-5 5zm0-8c-1.7 0-3 1.3-3 3s1.3 3 3 3 3-1.3 3-3-1.3-3-3-3z"/></svg>`,
        action: function () {
          if (!currentPostId) {
            const title = document.getElementById("post-title").value;
            const content = editor.getContent();
            savePost(content, title, currentPostId);
            setTimeout(() => {
              window.location.href = `/preview/${currentPostId}`;
            }, 500);
          } else {
            window.location.href = `/preview/${currentPostId}`;
          }
        },
        hotkey: "Mod-Shift-P",
      },
      "|",
      {
        name: "delete",
        title: "Delete Post",
        innerHTML: `<svg height="18" width="18"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>`,
        action: function () {
          if (currentPostId) {
            deletePost(currentPostId);
          } else {
            updateStatusMessage("No post to delete");
          }
        },
        visible: function () {
          return currentPostId !== null;
        },
      },
      "|",
      {
        name: "retract",
        title: "Retract Post",
        innerHTML: `<svg height="18" width="18"><path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/></svg>`,
        action: function () {
          if (currentPostId) {
            retractPost(currentPostId);
          } else {
            updateStatusMessage("No post to retract");
          }
        },
        visible: function () {
          return currentPostId !== null && currentPostPublished === true;
        },
      },
    ],
  });

  window.commandBarInstance = commandBar;

  setTimeout(() => refreshCommandBarVisibility(), 0);

  return commandBar;
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
      currentPostPublished = data.published || false;
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

const deletePost = (postID) => {
  if (!postID) {
    updateStatusMessage("No postID provided");
    return;
  }

  if (
    !confirm(
      "Are you sure you want to delete this post? This action cannot be undone.",
    )
  ) {
    return;
  }

  updateStatusMessage("Deleting...");

  const url = `/api/v1/post/${postID}/`;

  apiRequest(url, "DELETE")
    .then((response) => {
      if (response.status === 204) {
        updateStatusMessage("Post deleted");
        setTimeout(() => {
          window.location.href = "/dashboard";
        }, 1000);
      } else {
        updateStatusMessage("Delete failed");
      }
    })
    .catch((error) => {
      console.error("Delete error:", error);
      updateStatusMessage("Delete failed");
    });
};

const retractPost = (postID) => {
  if (!postID) {
    updateStatusMessage("No postID provided");
    return;
  }

  if (
    !confirm(
      "Are you sure you want to retract this post? It will no longer be visible to the public.",
    )
  ) {
    return;
  }

  updateStatusMessage("Retracting...");

  const url = `/api/v1/post/${postID}/`;
  const postData = {
    published: false,
    updated_on: lastKnownUpdateTime,
  };

  apiRequest(url, "PATCH", postData)
    .then((response) => {
      if (response.status === 200) {
        return response.json();
      } else if (response.status === 409) {
        updateStatusMessage(
          "Post was modified elsewhere. Reload to see changes.",
        );
        return Promise.reject("Conflict");
      } else {
        return Promise.reject("HTTP Error");
      }
    })
    .then((data) => {
      lastKnownUpdateTime = data.updated_on;
      updateStatusMessage("Post retracted");
      updatePublishedAndModified(data?.published, data?.updated_on);
    })
    .catch((error) => {
      if (error !== "Conflict") {
        console.error("Retract error:", error);
        updateStatusMessage("Retract failed");
      }
    });
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

    setTimeout(() => {
      statusMessage.textContent = "";
    }, 3000);
  }
};

const updatePublishedAndModified = (published, lastModifiedAt) => {
  const statusPublished = document.getElementById("status-published");
  const statusLastModified = document.getElementById("status-last-modified");

  currentPostPublished = published || false;
  statusPublished.innerText = published ? "Published" : "Draft";
  statusLastModified.innerText = lastModifiedAt ? lastModifiedAt : "";

  refreshCommandBarVisibility();

  return;
};

const refreshCommandBarVisibility = () => {
  const commandBar = document.getElementById("tinymde-commandbar");
  if (!commandBar) return;

  const deleteButton = commandBar.querySelector('[title="Delete Post"]');
  const retractButton = commandBar.querySelector('[title="Retract Post"]');

  if (deleteButton) {
    deleteButton.style.display = currentPostId !== null ? "" : "none";
  }

  if (retractButton) {
    retractButton.style.display =
      currentPostId !== null && currentPostPublished === true ? "" : "none";
  }
};

const setupImageDropHandling = (editor) => {
  editor.addEventListener("drop", function (event) {
    if (
      event.dataTransfer &&
      event.dataTransfer.files &&
      event.dataTransfer.files.length > 0
    ) {
      const files = event.dataTransfer.files;

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
