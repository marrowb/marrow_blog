---
title: "Malformed Test Post
excerpt: This frontmatter is missing a closing quote
tags: test,malformed
published: true
invalid_yaml: [unclosed bracket
---

# Malformed Test Post

This post has malformed YAML frontmatter that should cause parsing errors.

The frontmatter above has:
- Missing closing quote on title
- Unclosed bracket in invalid_yaml

## Test Content

Despite the malformed frontmatter, the markdown content itself is fine.

- List item 1
- List item 2

This tests error handling in the document processor.