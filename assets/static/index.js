import { initializeTinyMDE } from "./lib/utilsTinyMDE.js";

const app = () => {
  initializeTinyMDE();
};

document.addEventListener("DOMContentLoaded", app);
