export const initializeTinyMDE = () => {
  const editorHostElement = document.getElementById("editor");
  const commandBarHostElement = document.getElementById("tinymde-commandbar");

  if (editorHostElement && TinyMDE) {
    setupEditor();
    if (commandBarHostElement) {
      setupCommandBar();
    }
  }
};

const setupCommandBar = () => {
  new TinyMDE.CommandBar({
    element: commandBarHostElement,
    editor: editor,
  });
};

const setupEditor = () => {
  const editor = new TinyMDE.Editor({ element: editorHostElement });
  editor.addEventListener("change", function (event) {
    savePost();
  });
};

const savePost = (content, postID = null) => {
  fetch(route, {
    credentials: "include",
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: { content: content, postID: postID },
  })
    .then((response) => response.json())
    .then((id) => {
      // fetch the post ID
    })
    .catch((error) => {
      console.error("Error:", error);
    });
};
