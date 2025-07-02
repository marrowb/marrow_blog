import { apiRequest } from "./api.js";

export class TagInput {
  constructor(containerId, postId = null) {
    this.container = document.getElementById(containerId);
    this.postId = postId;
    this.tags = [];
    this.currentInput = "";
    this.saveTimeout = null;
    this.saveTimeoutLength = 1000;

    if (!this.container) {
      console.error(`Tag input container with id "${containerId}" not found`);
      return;
    }

    this.init();
  }

  init() {
    this.container.innerHTML = `
      <div class="tag-input-wrapper">
        <div class="tags-container" id="tags-container"></div>
        <input type="text"
               class="tag-input"
               id="tag-input"
               placeholder="Add tags..."
               autocomplete="off">
      </div>
    `;

    this.tagsContainer = this.container.querySelector("#tags-container");
    this.input = this.container.querySelector("#tag-input");

    this.setupEventListeners();
  }

  setupEventListeners() {
    this.input.addEventListener("keydown", (e) => {
      if (e.key === " " || e.key === "Enter") {
        e.preventDefault();
        this.addTag();
      } else if (e.key === "Backspace" && this.input.value === "" && this.tags.length > 0) {
        this.removeTag(this.tags.length - 1);
      }
    });

    this.input.addEventListener("input", (e) => {
      this.currentInput = e.target.value.trim();
    });

    this.input.addEventListener("blur", () => {
      if (this.currentInput) {
        this.addTag();
      }
    });
  }

  addTag() {
    const tagText = this.currentInput.trim().toLowerCase();

    if (tagText && !this.tags.includes(tagText)) {
      this.tags.push(tagText);
      this.input.value = "";
      this.currentInput = "";
      this.renderTags();
      this.scheduleSave();
    }
  }

  removeTag(index) {
    if (index >= 0 && index < this.tags.length) {
      this.tags.splice(index, 1);
      this.renderTags();
      this.scheduleSave();
    }
  }

  renderTags() {
    this.tagsContainer.innerHTML = "";

    this.tags.forEach((tag, index) => {
      const tagElement = document.createElement("span");
      tagElement.className = "tag-badge";
      tagElement.innerHTML = `
        ${tag}
        <button type="button" class="tag-remove" data-index="${index}">×</button>
      `;

      const removeBtn = tagElement.querySelector(".tag-remove");
      removeBtn.addEventListener("click", () => {
        this.removeTag(index);
      });

      this.tagsContainer.appendChild(tagElement);
    });
  }

  setTags(tagList) {
    this.tags = Array.isArray(tagList) ? [...tagList] : [];
    this.renderTags();
  }

  getTags() {
    return [...this.tags];
  }

  getTagsString() {
    return this.tags.join(",");
  }

  scheduleSave() {
    if (!this.postId) return;

    if (this.saveTimeout) {
      clearTimeout(this.saveTimeout);
    }

    this.saveTimeout = setTimeout(() => {
      this.saveTags();
    }, this.saveTimeoutLength);
  }

  saveTags() {
    if (!this.postId) return;

    const tagsString = this.getTagsString();

    apiRequest(`/api/v1/post/${this.postId}`, "PATCH", {
      tags: tagsString
    }).then(response => {
      if (response.ok) {
        console.log("Tags saved successfully");
      } else {
        console.error("Failed to save tags");
      }
    }).catch(error => {
      console.error("Error saving tags:", error);
    });
  }

  setPostId(postId) {
    this.postId = postId;
  }
}