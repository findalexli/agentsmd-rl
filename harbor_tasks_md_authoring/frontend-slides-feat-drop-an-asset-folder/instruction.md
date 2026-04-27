# feat: drop an asset folder, slides get prettier with images

Source: [zarazhangrui/frontend-slides#19](https://github.com/zarazhangrui/frontend-slides/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `SKILL.md`

## What to add / change

## What

Point the skill at an asset folder → it looks at each image, picks the good ones, and places them on the right slides. You just approve. Below are some examples of images inserted.

| | |
|---|---|
| ![Propose](https://github.com/user-attachments/assets/d8540b98-d68a-4b9a-b0c6-a6ce42515ed6) | ![Launch](https://github.com/user-attachments/assets/7784cf6d-22eb-4149-8be6-c1049ba7d992) |
| ![Data](https://github.com/user-attachments/assets/58884f04-b1e0-4c30-b780-3c7f69cc9133) | ![Monitor](https://github.com/user-attachments/assets/97905861-bb71-4560-b8d9-c81215c3ec7e) |

## How
Asks user if opt in to use images from assets
<img width="742" height="261" alt="Screenshot 2026-02-27 at 7 09 21 PM" src="https://github.com/user-attachments/assets/6575dfac-ac5d-43bc-877f-6870504624c7" />

Evaluate image usability
<img width="880" height="498" alt="Screenshot 2026-02-27 at 6 59 54 PM" src="https://github.com/user-attachments/assets/86d38a78-549b-4e2b-a79e-b2eacddd781f" />

- **Smart evaluation** — Claude views each image (multimodal), marks usable vs not, and co-designs the outline around them
- **Pillow processing** — circular crops, resizes, padding as needed per style
- **Direct file paths** — `<img src="assets/...">`

## Test plan
- [x] `/frontend-slides` with an image folder — images picked up and placed correctly
- [x] Without images — "No images" path works as before
- [x] Viewport fitting holds with images included

🤖 Generated with [Claude Code

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
