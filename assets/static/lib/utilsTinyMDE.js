export const initializeTinyMDE = () => {
  const editorHostElement = document.getElementById("editor");
  const commandBarHostElement = document.getElementById("tinymde-commandbar");

  if (editorHostElement && TinyMDE) {
    setupEditor(editorHostElement);
    if (commandBarHostElement) {
      setupCommandBar(commandBarHostElement, editorHostElement);
    }
  }
};

const setupCommandBar = (commandBarHostElement, editorHostElement) => {
  new TinyMDE.CommandBar({
    element: commandBarHostElement,
    editor: editor,
  });
};

const setupEditor = (editorHostElement) => {
  const editor = new TinyMDE.Editor({ element: editorHostElement });
  editor.addEventListener("change", function (event) {
    savePost();
  });
};

const savePost = (content, postID = null) => {
  fetch("/api/v1/post/", {
    credentials: "include",
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: { markdown_content: content, postID: postID },
  })
    .then((response) => response.json())
    .then((id) => {
      // fetch the post ID
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};
