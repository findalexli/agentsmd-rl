# Agent Config Files for gradio-mcp-tool-call-latency

Repo: gradio-app/gradio
Commit: b1f62c0ebc09be80aee830e26689ab70b939cf44
Files found: 5


---
## .agents/skills/gradio/SKILL.md

```
   1 | ---
   2 | name: gradio
   3 | description: Build Gradio web UIs and demos in Python. Use when creating or editing Gradio apps, components, event listeners, layouts, or chatbots.
   4 | ---
   5 | 
   6 | # Gradio
   7 | 
   8 | Gradio is a Python library for building interactive web UIs and ML demos. This skill covers the core API, patterns, and examples.
   9 | 
  10 | ## Guides
  11 | 
  12 | Detailed guides on specific topics (read these when relevant):
  13 | 
  14 | - [Quickstart](https://www.gradio.app/guides/quickstart)
  15 | - [The Interface Class](https://www.gradio.app/guides/the-interface-class)
  16 | - [Blocks and Event Listeners](https://www.gradio.app/guides/blocks-and-event-listeners)
  17 | - [Controlling Layout](https://www.gradio.app/guides/controlling-layout)
  18 | - [More Blocks Features](https://www.gradio.app/guides/more-blocks-features)
  19 | - [Custom CSS and JS](https://www.gradio.app/guides/custom-CSS-and-JS)
  20 | - [Streaming Outputs](https://www.gradio.app/guides/streaming-outputs)
  21 | - [Streaming Inputs](https://www.gradio.app/guides/streaming-inputs)
  22 | - [Sharing Your App](https://www.gradio.app/guides/sharing-your-app)
  23 | - [Custom HTML Components](https://www.gradio.app/guides/custom-HTML-components)
  24 | - [Getting Started with the Python Client](https://www.gradio.app/guides/getting-started-with-the-python-client)
  25 | - [Getting Started with the JS Client](https://www.gradio.app/guides/getting-started-with-the-js-client)
  26 | 
  27 | ## Core Patterns
  28 | 
  29 | **Interface** (high-level): wraps a function with input/output components.
  30 | 
  31 | ```python
  32 | import gradio as gr
  33 | 
  34 | def greet(name):
  35 |     return f"Hello {name}!"
  36 | 
  37 | gr.Interface(fn=greet, inputs="text", outputs="text").launch()
  38 | ```
  39 | 
  40 | **Blocks** (low-level): flexible layout with explicit event wiring.
  41 | 
  42 | ```python
  43 | import gradio as gr
  44 | 
  45 | with gr.Blocks() as demo:
  46 |     name = gr.Textbox(label="Name")
  47 |     output = gr.Textbox(label="Greeting")
  48 |     btn = gr.Button("Greet")
  49 |     btn.click(fn=lambda n: f"Hello {n}!", inputs=name, outputs=output)
  50 | 
  51 | demo.launch()
  52 | ```
  53 | 
  54 | **ChatInterface**: high-level wrapper for chatbot UIs.
  55 | 
  56 | ```python
  57 | import gradio as gr
  58 | 
  59 | def respond(message, history):
  60 |     return f"You said: {message}"
  61 | 
  62 | gr.ChatInterface(fn=respond).launch()
  63 | ```
  64 | 
  65 | ## Key Component Signatures
  66 | 
  67 | ### `Textbox(value: str | I18nData | Callable | None = None, type: Literal['text', 'password', 'email'] = "text", lines: int = 1, max_lines: int | None = None, placeholder: str | I18nData | None = None, label: str | I18nData | None = None, info: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, interactive: bool | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, autofocus: bool = False, autoscroll: bool = True, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", text_align: Literal['left', 'right'] | None = None, rtl: bool = False, buttons: list[Literal['copy'] | Button] | None = None, max_length: int | None = None, submit_btn: str | bool | None = False, stop_btn: str | bool | None = False, html_attributes: InputHTMLAttributes | None = None)`
  68 | Creates a textarea for user to enter string input or display string output..
  69 | 
  70 | ### `Number(value: float | Callable | None = None, label: str | I18nData | None = None, placeholder: str | I18nData | None = None, info: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, interactive: bool | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", buttons: list[Button] | None = None, precision: int | None = None, minimum: float | None = None, maximum: float | None = None, step: float = 1)`
  71 | Creates a numeric field for user to enter numbers as input or display numeric output..
  72 | 
  73 | ### `Slider(minimum: float = 0, maximum: float = 100, value: float | Callable | None = None, step: float | None = None, precision: int | None = None, label: str | I18nData | None = None, info: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, interactive: bool | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", randomize: bool = False, buttons: list[Literal['reset']] | None = None)`
  74 | Creates a slider that ranges from {minimum} to {maximum} with a step size of {step}..
  75 | 
  76 | ### `Checkbox(value: bool | Callable = False, label: str | I18nData | None = None, info: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, interactive: bool | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", buttons: list[Button] | None = None)`
  77 | Creates a checkbox that can be set to `True` or `False`.
  78 | 
  79 | ### `Dropdown(choices: Sequence[str | int | float | tuple[str, str | int | float]] | None = None, value: str | int | float | Sequence[str | int | float] | Callable | DefaultValue | None = DefaultValue(), type: Literal['value', 'index'] = "value", multiselect: bool | None = None, allow_custom_value: bool = False, max_choices: int | None = None, filterable: bool = True, label: str | I18nData | None = None, info: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, interactive: bool | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", buttons: list[Button] | None = None)`
  80 | Creates a dropdown of choices from which a single entry or multiple entries can be selected (as an input component) or displayed (as an output component)..
  81 | 
  82 | ### `Radio(choices: Sequence[str | int | float | tuple[str, str | int | float]] | None = None, value: str | int | float | Callable | None = None, type: Literal['value', 'index'] = "value", label: str | I18nData | None = None, info: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, interactive: bool | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", rtl: bool = False, buttons: list[Button] | None = None)`
  83 | Creates a set of (string or numeric type) radio buttons of which only one can be selected..
  84 | 
  85 | ### `Image(value: str | PIL.Image.Image | np.ndarray | Callable | None = None, format: str = "webp", height: int | str | None = None, width: int | str | None = None, image_mode: Literal['1', 'L', 'P', 'RGB', 'RGBA', 'CMYK', 'YCbCr', 'LAB', 'HSV', 'I', 'F'] | None = "RGB", sources: list[Literal['upload', 'webcam', 'clipboard']] | Literal['upload', 'webcam', 'clipboard'] | None = None, type: Literal['numpy', 'pil', 'filepath'] = "numpy", label: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, buttons: list[Literal['download', 'share', 'fullscreen'] | Button] | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, interactive: bool | None = None, visible: bool | Literal['hidden'] = True, streaming: bool = False, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", webcam_options: WebcamOptions | None = None, placeholder: str | None = None, watermark: WatermarkOptions | None = None)`
  86 | Creates an image component that can be used to upload images (as an input) or display images (as an output)..
  87 | 
  88 | ### `Audio(value: str | Path | tuple[int, np.ndarray] | Callable | None = None, sources: list[Literal['upload', 'microphone']] | Literal['upload', 'microphone'] | None = None, type: Literal['numpy', 'filepath'] = "numpy", label: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, interactive: bool | None = None, visible: bool | Literal['hidden'] = True, streaming: bool = False, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", format: Literal['wav', 'mp3'] | None = None, autoplay: bool = False, editable: bool = True, buttons: list[Literal['download', 'share'] | Button] | None = None, waveform_options: WaveformOptions | dict | None = None, loop: bool = False, recording: bool = False, subtitles: str | Path | list[dict[str, Any]] | None = None, playback_position: float = 0)`
  89 | Creates an audio component that can be used to upload/record audio (as an input) or display audio (as an output)..
  90 | 
  91 | ### `Video(value: str | Path | Callable | None = None, format: str | None = None, sources: list[Literal['upload', 'webcam']] | Literal['upload', 'webcam'] | None = None, height: int | str | None = None, width: int | str | None = None, label: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, interactive: bool | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", webcam_options: WebcamOptions | None = None, include_audio: bool | None = None, autoplay: bool = False, buttons: list[Literal['download', 'share'] | Button] | None = None, loop: bool = False, streaming: bool = False, watermark: WatermarkOptions | None = None, subtitles: str | Path | list[dict[str, Any]] | None = None, playback_position: float = 0)`
  92 | Creates a video component that can be used to upload/record videos (as an input) or display videos (as an output).
  93 | 
  94 | ### `File(value: str | list[str] | Callable | None = None, file_count: Literal['single', 'multiple', 'directory'] = "single", file_types: list[str] | None = None, type: Literal['filepath', 'binary'] = "filepath", label: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, height: int | str | float | None = None, interactive: bool | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", allow_reordering: bool = False, buttons: list[Button] | None = None)`
  95 | Creates a file component that allows uploading one or more generic files (when used as an input) or displaying generic files or URLs for download (as output).
  96 | 
  97 | ### `Chatbot(value: list[MessageDict | Message] | Callable | None = None, label: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, container: bool = True, scale: int | None = None, min_width: int = 160, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, autoscroll: bool = True, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", height: int | str | None = 400, resizable: bool = False, max_height: int | str | None = None, min_height: int | str | None = None, editable: Literal['user', 'all'] | None = None, latex_delimiters: list[dict[str, str | bool]] | None = None, rtl: bool = False, buttons: list[Literal['share', 'copy', 'copy_all'] | Button] | None = None, watermark: str | None = None, avatar_images: tuple[str | Path | None, str | Path | None] | None = None, sanitize_html: bool = True, render_markdown: bool = True, feedback_options: list[str] | tuple[str, ...] | None = ('Like', 'Dislike'), feedback_value: Sequence[str | None] | None = None, line_breaks: bool = True, layout: Literal['panel', 'bubble'] | None = None, placeholder: str | None = None, examples: list[ExampleMessage] | None = None, allow_file_downloads: <class 'inspect._empty'> = True, group_consecutive_messages: bool = True, allow_tags: list[str] | bool = True, reasoning_tags: list[tuple[str, str]] | None = None, like_user_message: bool = False)`
  98 | Creates a chatbot that displays user-submitted messages and responses.
  99 | 
 100 | ### `Button(value: str | I18nData | Callable = "Run", every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, variant: Literal['primary', 'secondary', 'stop', 'huggingface'] = "secondary", size: Literal['sm', 'md', 'lg'] = "lg", icon: str | Path | None = None, link: str | None = None, link_target: Literal['_self', '_blank', '_parent', '_top'] = "_self", visible: bool | Literal['hidden'] = True, interactive: bool = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", scale: int | None = None, min_width: int | None = None)`
 101 | Creates a button that can be assigned arbitrary .click() events.
 102 | 
 103 | ### `Markdown(value: str | I18nData | Callable | None = None, label: str | I18nData | None = None, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool | None = None, rtl: bool = False, latex_delimiters: list[dict[str, str | bool]] | None = None, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", sanitize_html: bool = True, line_breaks: bool = False, header_links: bool = False, height: int | str | None = None, max_height: int | str | None = None, min_height: int | str | None = None, buttons: list[Literal['copy']] | None = None, container: bool = False, padding: bool = False)`
 104 | Used to render arbitrary Markdown output.
 105 | 
 106 | ### `HTML(value: Any | Callable | None = None, label: str | I18nData | None = None, html_template: str = "${value}", css_template: str = "", js_on_load: str | None = "element.addEventListener('click', function() { trigger('click') });", apply_default_css: bool = True, every: Timer | float | None = None, inputs: Component | Sequence[Component] | set[Component] | None = None, show_label: bool = False, visible: bool | Literal['hidden'] = True, elem_id: str | None = None, elem_classes: list[str] | str | None = None, render: bool = True, key: int | str | tuple[int | str, ...] | None = None, preserved_by_key: list[str] | str | None = "value", min_height: int | None = None, max_height: int | None = None, container: bool = False, padding: bool = False, autoscroll: bool = False, buttons: list[Button] | None = None, server_functions: list[Callable] | None = None, props: Any)`
 107 | Creates a component with arbitrary HTML.
 108 | 
 109 | 
 110 | ## Custom HTML Components
 111 | 
 112 | If a task requires significant customization of an existing component or a component that doesn't exist in Gradio, you can create one with `gr.HTML`. It supports `html_template` (with `${}` JS expressions and `{{}}` Handlebars syntax), `css_template` for scoped styles, and `js_on_load` for interactivity — where `props.value` updates the component value and `trigger('event_name')` fires Gradio events. For reuse, subclass `gr.HTML` and define `api_info()` for API/MCP support. See the [full guide](https://www.gradio.app/guides/custom-HTML-components).
 113 | 
 114 | Here's an example that shows how to create and use these kinds of components:
 115 | 
 116 | ```python
 117 | import gradio as gr
 118 | 
 119 | class StarRating(gr.HTML):
 120 |     def __init__(self, label, value=0, **kwargs):
 121 |         html_template = """
 122 |         <h2>${label} rating:</h2>
 123 |         ${Array.from({length: 5}, (_, i) => `<img class='${i < value ? '' : 'faded'}' src='https://upload.wikimedia.org/wikipedia/commons/d/df/Award-star-gold-3d.svg'>`).join('')}
 124 |         """
 125 |         css_template = """
 126 |             img { height: 50px; display: inline-block; cursor: pointer; }
 127 |             .faded { filter: grayscale(100%); opacity: 0.3; }
 128 |         """
 129 |         js_on_load = """
 130 |             const imgs = element.querySelectorAll('img');
 131 |             imgs.forEach((img, index) => {
 132 |                 img.addEventListener('click', () => {
 133 |                     props.value = index + 1;
 134 |                 });
 135 |             });
 136 |         """
 137 |         super().__init__(value=value, label=label, html_template=html_template, css_template=css_template, js_on_load=js_on_load, **kwargs)
 138 | 
 139 |     def api_info(self):
 140 |         return {"type": "integer", "minimum": 0, "maximum": 5}
 141 | 
 142 | 
 143 | with gr.Blocks() as demo:
 144 |     gr.Markdown("# Restaurant Review")
 145 |     food_rating = StarRating(label="Food", value=3)
 146 |     service_rating = StarRating(label="Service", value=3)
 147 |     ambience_rating = StarRating(label="Ambience", value=3)
 148 |     average_btn = gr.Button("Calculate Average Rating")
 149 |     rating_output = StarRating(label="Average", value=3)
 150 |     def calculate_average(food, service, ambience):
 151 |         return round((food + service + ambience) / 3)
 152 |     average_btn.click(
 153 |         fn=calculate_average,
 154 |         inputs=[food_rating, service_rating, ambience_rating],
 155 |         outputs=rating_output
 156 |     )
 157 | 
 158 | demo.launch()
 159 | ```
 160 | 
 161 | ## Event Listeners
 162 | 
 163 | All event listeners share the same signature:
 164 | 
 165 | ```python
 166 | component.event_name(
 167 |     fn: Callable | None | Literal["decorator"] = "decorator",
 168 |     inputs: Component | Sequence[Component] | set[Component] | None = None,
 169 |     outputs: Component | Sequence[Component] | set[Component] | None = None,
 170 |     api_name: str | None = None,
 171 |     api_description: str | None | Literal[False] = None,
 172 |     scroll_to_output: bool = False,
 173 |     show_progress: Literal["full", "minimal", "hidden"] = "full",
 174 |     show_progress_on: Component | Sequence[Component] | None = None,
 175 |     queue: bool = True,
 176 |     batch: bool = False,
 177 |     max_batch_size: int = 4,
 178 |     preprocess: bool = True,
 179 |     postprocess: bool = True,
 180 |     cancels: dict[str, Any] | list[dict[str, Any]] | None = None,
 181 |     trigger_mode: Literal["once", "multiple", "always_last"] | None = None,
 182 |     js: str | Literal[True] | None = None,
 183 |     concurrency_limit: int | None | Literal["default"] = "default",
 184 |     concurrency_id: str | None = None,
 185 |     api_visibility: Literal["public", "private", "undocumented"] = "public",
 186 |     time_limit: int | None = None,
 187 |     stream_every: float = 0.5,
 188 |     key: int | str | tuple[int | str, ...] | None = None,
 189 |     validator: Callable | None = None,
 190 | ) -> Dependency
 191 | ```
 192 | 
 193 | Supported events per component:
 194 | 
 195 | - **AnnotatedImage**: select
 196 | - **Audio**: stream, change, clear, play, pause, stop, pause, start_recording, pause_recording, stop_recording, upload, input
 197 | - **BarPlot**: select, double_click
 198 | - **BrowserState**: change
 199 | - **Button**: click
 200 | - **Chatbot**: change, select, like, retry, undo, example_select, option_select, clear, copy, edit
 201 | - **Checkbox**: change, input, select
 202 | - **CheckboxGroup**: change, input, select
 203 | - **ClearButton**: click
 204 | - **Code**: change, input, focus, blur
 205 | - **ColorPicker**: change, input, submit, focus, blur
 206 | - **Dataframe**: change, input, select, edit
 207 | - **Dataset**: click, select
 208 | - **DateTime**: change, submit
 209 | - **DeepLinkButton**: click
 210 | - **Dialogue**: change, input, submit
 211 | - **DownloadButton**: click
 212 | - **Dropdown**: change, input, select, focus, blur, key_up
 213 | - **DuplicateButton**: click
 214 | - **File**: change, select, clear, upload, delete, download
 215 | - **FileExplorer**: change, input, select
 216 | - **Gallery**: select, upload, change, delete, preview_close, preview_open
 217 | - **HTML**: change, input, click, double_click, submit, stop, edit, clear, play, pause, end, start_recording, pause_recording, stop_recording, focus, blur, upload, release, select, stream, like, example_select, option_select, load, key_up, apply, delete, tick, undo, retry, expand, collapse, download, copy
 218 | - **HighlightedText**: change, select
 219 | - **Image**: clear, change, stream, select, upload, input
 220 | - **ImageEditor**: clear, change, input, select, upload, apply
 221 | - **ImageSlider**: clear, change, stream, select, upload, input
 222 | - **JSON**: change
 223 | - **Label**: change, select
 224 | - **LinePlot**: select, double_click
 225 | - **LoginButton**: click
 226 | - **Markdown**: change, copy
 227 | - **Model3D**: change, upload, edit, clear
 228 | - **MultimodalTextbox**: change, input, select, submit, focus, blur, stop
 229 | - **Navbar**: change
 230 | - **Number**: change, input, submit, focus, blur
 231 | - **ParamViewer**: change, upload
 232 | - **Plot**: change
 233 | - **Radio**: select, change, input
 234 | - **ScatterPlot**: select, double_click
 235 | - **SimpleImage**: clear, change, upload
 236 | - **Slider**: change, input, release
 237 | - **State**: change
 238 | - **Textbox**: change, input, select, submit, focus, blur, stop, copy
 239 | - **Timer**: tick
 240 | - **UploadButton**: click, upload
 241 | - **Video**: change, clear, start_recording, stop_recording, stop, play, pause, end, upload, input
 242 | 
 243 | ## Additional Reference
 244 | 
 245 | - [End-to-End Examples](examples.md) — complete working apps
```


---
## AGENTS.md

```
   1 | # AGENTS.md
   2 | 
   3 | Instructions for AI coding agents working on this repository.
   4 | 
   5 | ## Repository Structure
   6 | 
   7 | - `gradio/` — Python source for the Gradio library (backend)
   8 |   - `gradio/components/` — all Gradio components
   9 |   - `gradio/cli/` — CLI commands (`gradio`, `gradio cc`, `gradio skills`, etc.)
  10 | - `client/python/` — the `gradio_client` Python client library
  11 | - `client/js/` — the `@gradio/client` JavaScript client library
  12 | - `js/` — frontend code (Svelte/TypeScript), with each component in its own subdirectory
  13 | - `test/` — Python backend tests (pytest)
  14 | - `js/spa/test/` — browser/Playwright tests (`*.spec.ts`)
  15 | - `demo/` — example Gradio apps
  16 | - `guides/` — written guides and tutorials for the website
  17 | 
  18 | ## Pull Request Rules
  19 | 
  20 | Follow these rules when creating or contributing to pull requests:
  21 | 
  22 | 1. **Target an issue.** Every non-trivial PR should reference an existing GitHub issue. If one doesn't exist, create it first. PRs without a linked issue may be closed.
  23 | 
  24 | 2. **Use the PR template.** Fill out every section of `.github/PULL_REQUEST_TEMPLATE.md`, including:
  25 |    - A clear description of the change
  26 |    - The AI disclosure checkbox (see below)
  27 |    - The linked issue (`Closes: #NNN`)
  28 | 
  29 | 3. **AI disclosure is mandatory.** If AI was used in any non-trivial way (drafting code, writing the PR description, etc.), you must disclose this in the PR template. Trivial autocomplete does not need to be disclosed. All AI-generated code must be self-reviewed.
  30 | 
  31 | 4. **Format your code before pushing.**
  32 |    - Backend: `bash scripts/format_backend.sh`
  33 |    - Frontend: `bash scripts/format_frontend.sh`
  34 | 
  35 | 5. **Tests must pass.** PRs are only merged when CI is green. Run backend tests locally with `bash scripts/run_backend_tests.sh`.
  36 | 
  37 | 6. **PR title and description should be clear and written in English.** The title should concisely describe *what* the PR does. The description should explain *why*.
  38 | 
  39 | 7. **Submit against `main`.** All PRs target the `main` branch.
  40 | 
  41 | ## Code Style
  42 | 
  43 | - Python code is formatted with `ruff`. Run `bash scripts/format_backend.sh`.
  44 | - Frontend code is formatted with `prettier`. Run `bash scripts/format_frontend.sh`.
  45 | - Be consistent with the style of the surrounding code.
  46 | 
  47 | ## More Details
  48 | 
  49 | See [CONTRIBUTING.md](CONTRIBUTING.md) for full setup instructions, testing details, and the contribution workflow.
```


---
## README.md

```
   1 | <!-- DO NOT EDIT THIS FILE DIRECTLY. INSTEAD EDIT THE `readme_template.md` OR `guides/01_getting-started/01_quickstart.md` TEMPLATES AND THEN RUN `render_readme.py` SCRIPT. -->
   2 | 
   3 | <div align="center">
   4 | <a href="https://gradio.app">
   5 | <img src="readme_files/gradio.svg" alt="gradio" width=350>
   6 | </a>
   7 | </div>
   8 | 
   9 | <div align="center">
  10 | <span>
  11 | <a href="https://www.producthunt.com/posts/gradio-5-0?embed=true&utm_source=badge-featured&utm_medium=badge&utm_souce=badge-gradio&#0045;5&#0045;0" target="_blank"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=501906&theme=light" alt="Gradio&#0032;5&#0046;0 - the&#0032;easiest&#0032;way&#0032;to&#0032;build&#0032;AI&#0032;web&#0032;apps | Product Hunt" style="width: 150px; height: 54px;" width="150" height="54" /></a>
  12 | <a href="https://trendshift.io/repositories/2145" target="_blank"><img src="https://trendshift.io/api/badge/repositories/2145" alt="gradio-app%2Fgradio | Trendshift" style="width: 150px; height: 55px;" width="150" height="55"/></a>
  13 | </span>
  14 | 
  15 | [![gradio-backend](https://github.com/gradio-app/gradio/actions/workflows/test-python.yml/badge.svg)](https://github.com/gradio-app/gradio/actions/workflows/test-python.yml)
  16 | [![gradio-ui](https://github.com/gradio-app/gradio/actions/workflows/tests-js.yml/badge.svg)](https://github.com/gradio-app/gradio/actions/workflows/tests-js.yml) 
  17 | [![PyPI](https://img.shields.io/pypi/v/gradio)](https://pypi.org/project/gradio/)
  18 | [![PyPI downloads](https://img.shields.io/pypi/dm/gradio)](https://pypi.org/project/gradio/)
  19 | ![Python version](https://img.shields.io/badge/python-3.10+-important)
  20 | [![Twitter follow](https://img.shields.io/twitter/follow/gradio?style=social&label=follow)](https://twitter.com/gradio)
  21 | 
  22 | [Website](https://gradio.app)
  23 | | [Documentation](https://gradio.app/docs/)
  24 | | [Guides](https://gradio.app/guides/)
  25 | | [Getting Started](https://gradio.app/getting_started/)
  26 | | [Examples](demo/)
  27 | 
  28 | </div>
  29 | 
  30 | <div align="center">
  31 | 
  32 | English | [中文](readme_files/zh-cn#readme)
  33 | 
  34 | </div>
  35 | 
  36 | # Gradio: Build Machine Learning Web Apps — in Python
  37 | 
  38 | 
  39 | 
  40 | Gradio is an open-source Python package that allows you to quickly **build** a demo or web application for your machine learning model, API, or any arbitrary Python function. You can then **share** a link to your demo or web application in just a few seconds using Gradio's built-in sharing features. *No JavaScript, CSS, or web hosting experience needed!*
  41 | 
  42 | <img src="https://huggingface.co/datasets/huggingface/documentation-images/resolve/main/gradio-guides/gif-version.gif" style="padding-bottom: 10px">
  43 | 
  44 | It just takes a few lines of Python to create your own demo, so let's get started 💫
  45 | 
  46 | 
  47 | ### Installation
  48 | 
  49 | **Prerequisite**: Gradio requires [Python 3.10 or higher](https://www.python.org/downloads/).
  50 | 
  51 | 
  52 | We recommend installing Gradio using `pip`, which is included by default in Python. Run this in your terminal or command prompt:
  53 | 
  54 | ```bash
  55 | pip install --upgrade gradio
  56 | ```
  57 | 
  58 | 
  59 | > [!TIP]
  60 |  > It is best to install Gradio in a virtual environment. Detailed installation instructions for all common operating systems <a href="https://www.gradio.app/main/guides/installing-gradio-in-a-virtual-environment">are provided here</a>. 
  61 | 
  62 | ### Building Your First Demo
  63 | 
  64 | You can run Gradio in your favorite code editor, Jupyter notebook, Google Colab, or anywhere else you write Python. Let's write your first Gradio app:
  65 | 
  66 | 
  67 | ```python
  68 | import gradio as gr
  69 | 
  70 | def greet(name, intensity):
  71 |     return "Hello, " + name + "!" * int(intensity)
  72 | 
  73 | demo = gr.Interface(
  74 |     fn=greet,
  75 |     inputs=["text", "slider"],
  76 |     outputs=["text"],
  77 |     api_name="predict"
  78 | )
  79 | 
  80 | demo.launch()
  81 | ```
  82 | 
  83 | 
  84 | 
  85 | > [!TIP]
  86 |  > We shorten the imported name from <code>gradio</code> to <code>gr</code>. This is a widely adopted convention for better readability of code. 
  87 | 
  88 | Now, run your code. If you've written the Python code in a file named `app.py`, then you would run `python app.py` from the terminal.
  89 | 
  90 | The demo below will open in a browser on [http://localhost:7860](http://localhost:7860) if running from a file. If you are running within a notebook, the demo will appear embedded within the notebook.
  91 | 
  92 | ![`hello_world_4` demo](demo/hello_world_4/screenshot.gif)
  93 | 
  94 | Type your name in the textbox on the left, drag the slider, and then press the Submit button. You should see a friendly greeting on the right.
  95 | 
  96 | > [!TIP]
  97 |  > When developing locally, you can run your Gradio app in <strong>hot reload mode</strong>, which automatically reloads the Gradio app whenever you make changes to the file. To do this, simply type in <code>gradio</code> before the name of the file instead of <code>python</code>. In the example above, you would type: `gradio app.py` in your terminal. You can also enable <strong>vibe mode</strong> by using the <code>--vibe</code> flag, e.g. <code>gradio --vibe app.py</code>, which provides an in-browser chat that can be used to write or edit your Gradio app using natural language. Learn more in the <a href="https://www.gradio.app/guides/developing-faster-with-reload-mode">Hot Reloading Guide</a>.
  98 | 
  99 | 
 100 | **Understanding the `Interface` Class**
 101 | 
 102 | You'll notice that in order to make your first demo, you created an instance of the `gr.Interface` class. The `Interface` class is designed to create demos for machine learning models which accept one or more inputs, and return one or more outputs. 
 103 | 
 104 | The `Interface` class has three core arguments:
 105 | 
 106 | - `fn`: the function to wrap a user interface (UI) around
 107 | - `inputs`: the Gradio component(s) to use for the input. The number of components should match the number of arguments in your function.
 108 | - `outputs`: the Gradio component(s) to use for the output. The number of components should match the number of return values from your function.
 109 | 
 110 | The `fn` argument is very flexible -- you can pass *any* Python function that you want to wrap with a UI. In the example above, we saw a relatively simple function, but the function could be anything from a music generator to a tax calculator to the prediction function of a pretrained machine learning model.
 111 | 
 112 | The `inputs` and `outputs` arguments take one or more Gradio components. As we'll see, Gradio includes more than [30 built-in components](https://www.gradio.app/docs/gradio/introduction) (such as the `gr.Textbox()`, `gr.Image()`, and `gr.HTML()` components) that are designed for machine learning applications. 
 113 | 
 114 | > [!TIP]
 115 |  > For the `inputs` and `outputs` arguments, you can pass in the name of these components as a string (`"textbox"`) or an instance of the class (`gr.Textbox()`).
 116 | 
 117 | If your function accepts more than one argument, as is the case above, pass a list of input components to `inputs`, with each input component corresponding to one of the arguments of the function, in order. The same holds true if your function returns more than one value: simply pass in a list of components to `outputs`. This flexibility makes the `Interface` class a very powerful way to create demos.
 118 | 
 119 | We'll dive deeper into the `gr.Interface` on our series on [building Interfaces](https://www.gradio.app/main/guides/the-interface-class).
 120 | 
 121 | ### Sharing Your Demo
 122 | 
 123 | What good is a beautiful demo if you can't share it? Gradio lets you easily share a machine learning demo without having to worry about the hassle of hosting on a web server. Simply set `share=True` in `launch()`, and a publicly accessible URL will be created for your demo. Let's revisit our example demo,  but change the last line as follows:
 124 | 
 125 | ```python
 126 | import gradio as gr
 127 | 
 128 | def greet(name):
 129 |     return "Hello " + name + "!"
 130 | 
 131 | demo = gr.Interface(fn=greet, inputs="textbox", outputs="textbox")
 132 |     
 133 | demo.launch(share=True)  # Share your demo with just 1 extra parameter 🚀
 134 | ```
 135 | 
 136 | When you run this code, a public URL will be generated for your demo in a matter of seconds, something like:
 137 | 
 138 | 👉 &nbsp; `https://a23dsf231adb.gradio.live`
 139 | 
 140 | Now, anyone around the world can try your Gradio demo from their browser, while the machine learning model and all computation continues to run locally on your computer.
 141 | 
 142 | To learn more about sharing your demo, read our dedicated guide on [sharing your Gradio application](https://www.gradio.app/guides/sharing-your-app).
 143 | 
 144 | 
 145 | ### An Overview of Gradio
 146 | 
 147 | So far, we've been discussing the `Interface` class, which is a high-level class that lets you build demos quickly with Gradio. But what else does Gradio include?
 148 | 
 149 | #### Custom Demos with `gr.Blocks`
 150 | 
 151 | Gradio offers a low-level approach for designing web apps with more customizable layouts and data flows with the `gr.Blocks` class. Blocks supports things like controlling where components appear on the page, handling multiple data flows and more complex interactions (e.g. outputs can serve as inputs to other functions), and updating properties/visibility of components based on user interaction — still all in Python. 
 152 | 
 153 | You can build very custom and complex applications using `gr.Blocks()`. For example, the popular image generation [Automatic1111 Web UI](https://github.com/AUTOMATIC1111/stable-diffusion-webui) is built using Gradio Blocks. We dive deeper into the `gr.Blocks` on our series on [building with Blocks](https://www.gradio.app/guides/blocks-and-event-listeners).
 154 | 
 155 | #### Chatbots with `gr.ChatInterface`
 156 | 
 157 | Gradio includes another high-level class, `gr.ChatInterface`, which is specifically designed to create Chatbot UIs. Similar to `Interface`, you supply a function and Gradio creates a fully working Chatbot UI. If you're interested in creating a chatbot, you can jump straight to [our dedicated guide on `gr.ChatInterface`](https://www.gradio.app/guides/creating-a-chatbot-fast).
 158 | 
 159 | #### The Gradio Python & JavaScript Ecosystem
 160 | 
 161 | That's the gist of the core `gradio` Python library, but Gradio is actually so much more! It's an entire ecosystem of Python and JavaScript libraries that let you build machine learning applications, or query them programmatically, in Python or JavaScript. Here are other related parts of the Gradio ecosystem:
 162 | 
 163 | * [Gradio Python Client](https://www.gradio.app/guides/getting-started-with-the-python-client) (`gradio_client`): query any Gradio app programmatically in Python.
 164 | * [Gradio JavaScript Client](https://www.gradio.app/guides/getting-started-with-the-js-client) (`@gradio/client`): query any Gradio app programmatically in JavaScript.
 165 | * [Hugging Face Spaces](https://huggingface.co/spaces): the most popular place to host Gradio applications — for free!
 166 | 
 167 | ### What's Next?
 168 | 
 169 | Keep learning about Gradio sequentially using the Gradio Guides, which include explanations as well as example code and embedded interactive demos. Next up: [let's dive deeper into the Interface class](https://www.gradio.app/guides/the-interface-class).
 170 | 
 171 | Or, if you already know the basics and are looking for something specific, you can search the more [technical API documentation](https://www.gradio.app/docs/).
 172 | 
 173 | 
 174 | ### AI Coding Skills
 175 | 
 176 | Gradio provides a "skill" that enriches AI coding assistants (like Cursor, Claude Code, Codex, etc.) with Gradio-specific knowledge, so that they can build Gradio apps more effectively. This is especially useful when creating custom Gradio components or styling. Install the Gradio skill for your coding assistant with a single command:
 177 | 
 178 | ```bash
 179 | gradio skills add --cursor   # or --claude, --codex, --opencode
 180 | ```
 181 | 
 182 | Use `--global` to install at the user level (applies to all projects). Your skill will be automatically available for the particular coding agent.
 183 | 
 184 | You can also install a skill for a **specific Gradio Space**, which generates API usage docs (Python, JS, cURL) on the fly:
 185 | 
 186 | ```bash
 187 | gradio skills add abidlabs/en2fr --cursor
 188 | ```
 189 | 
 190 | ## Questions?
 191 | 
 192 | If you'd like to report a bug or have a feature request, please create an [issue on GitHub](https://github.com/gradio-app/gradio/issues/new/choose). For general questions about usage, we are available on [our Discord server](https://discord.com/invite/feTf9x3ZSB) and happy to help.
 193 | 
 194 | If you like Gradio, please leave us a ⭐ on GitHub!
 195 | 
 196 | ## Open Source Stack
 197 | 
 198 | Gradio is built on top of many wonderful open-source libraries!
 199 | 
 200 | [<img src="readme_files/huggingface_mini.svg" alt="huggingface" height=40>](https://huggingface.co)
 201 | [<img src="readme_files/python.svg" alt="python" height=40>](https://www.python.org)
 202 | [<img src="readme_files/fastapi.svg" alt="fastapi" height=40>](https://fastapi.tiangolo.com)
 203 | [<img src="readme_files/encode.svg" alt="encode" height=40>](https://www.encode.io)
 204 | [<img src="readme_files/svelte.svg" alt="svelte" height=40>](https://svelte.dev)
 205 | [<img src="readme_files/vite.svg" alt="vite" height=40>](https://vitejs.dev)
 206 | [<img src="readme_files/pnpm.svg" alt="pnpm" height=40>](https://pnpm.io)
 207 | [<img src="readme_files/tailwind.svg" alt="tailwind" height=40>](https://tailwindcss.com)
 208 | [<img src="readme_files/storybook.svg" alt="storybook" height=40>](https://storybook.js.org/)
 209 | [<img src="readme_files/chromatic.svg" alt="chromatic" height=40>](https://www.chromatic.com/)
 210 | 
 211 | ## License
 212 | 
 213 | Gradio is licensed under the Apache License 2.0 found in the [LICENSE](LICENSE) file in the root directory of this repository.
 214 | 
 215 | ## Citation
 216 | 
 217 | Also check out the paper _[Gradio: Hassle-Free Sharing and Testing of ML Models in the Wild](https://arxiv.org/abs/1906.02569), ICML HILL 2019_, and please cite it if you use Gradio in your work.
 218 | 
 219 | ```
 220 | @article{abid2019gradio,
 221 |   title = {Gradio: Hassle-Free Sharing and Testing of ML Models in the Wild},
 222 |   author = {Abid, Abubakar and Abdalla, Ali and Abid, Ali and Khan, Dawood and Alfozan, Abdulrahman and Zou, James},
 223 |   journal = {arXiv preprint arXiv:1906.02569},
 224 |   year = {2019},
 225 | }
 226 | ```
```


---
## gradio/cli/commands/components/files/README.md

```
   1 | ---
   2 | tags: [gradio-custom-component<<template>><<tags>>]
   3 | title: <<title>>
   4 | short_description: <<short-description>>
   5 | colorFrom: blue
   6 | colorTo: yellow
   7 | sdk: gradio
   8 | pinned: false
   9 | app_file: space.py
  10 | ---
  11 | 
  12 | # <<title>>
  13 | 
  14 | You can auto-generate documentation for your custom component with the `gradio cc docs` command.
  15 | You can also edit this file however you like.
```


---
## gradio/icons/README.md

```
   1 | The icons in this directory are loaded via `gradio.utils.get_icon_path` and
   2 | can be used directly in backend code (e.g. to populate icons in components).
```
