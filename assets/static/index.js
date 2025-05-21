import { TinyMDE } from "./lib/imports.js"; // Adjusted path to './lib/imports.js'
import { initializeTinyMDE } from "./lib/utilsTinyMDE.js";

const app = () => {
  initializeTinyMDE();
};

document.addEventListener("DOMContentLoaded", app);
