import { TinyMDE } from "./lib/imports.js"; // Adjusted path to './lib/imports.js'

const initializeTinyMDE = () => {
  const editorHostElement = document.getElementById("editor");
  const commandBarHostElement = document.getElementById("tinymde-commandbar");

  if (editorHostElement && TinyMDE) {
    const editor = new TinyMDE.Editor({ element: editorHostElement });

    if (commandBarHostElement) {
      new TinyMDE.CommandBar({
        element: commandBarHostElement,
        editor: editor,
      });
    }
  }
};

const app = () => {
  initializeTinyMDE();
};

document.addEventListener("DOMContentLoaded", app);
