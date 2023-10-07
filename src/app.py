from flask import Flask, render_template

app = Flask(__name__)


def _get_base_params() -> dict[str, str]:
    """Returns the base parameters later utilized by the Flask App."""
    return {
        "color": "#98CCEB",
        "secondary_color": "#0D1117",
        "red_color": "#FFB3B3",
        "green_color": "#B3FFB3",
        "name": "Shayaan"
    }


@app.route("/")
def home():
    return render_template(
        "index.html",
        base=_get_base_params(),
        metric_deltas={"temperature": 1, "dewpoint": -10, "relative_humidity": -40}
    )


if __name__ == '__main__':
    app.run(debug=True)