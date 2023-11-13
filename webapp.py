import base64
from io import BytesIO

from flask import (
    Flask,
    render_template,
    request,
    )
from sympy import symbols

from consumer import ConsumerProblem

app = Flask(__name__)

def convert_to_mathml(html: str) -> str:
    """


    Parameters
    ----------
    html : str
        HTML that includes the Python parameters 'a', 'p', 'px', 'py', 'm'.

    Returns
    -------
    str
        The same HTML with the parameters mentioned above converted to MathML.

    """

    MATHML_DICT = {
        "'a'": """<math><mi>a</mi></math>""",
        "'p'": "<math><mi>&rho;</mi></math>",
        "'m'": "<math><mi>m</mi></math>",
        "'px'": """<math>
                        <msub>
                            <mi>p</mi>
                            <mi>x</mi>
                        </msub>
                    </math>""",
        "'py'": """<math>
                        <msub>
                            <mi>p</mi>
                            <mi>y</mi>
                        </msub>
                    </math>""",
        "'m'": "<math><mi>m</mi></math>",
        }

    for key, value in MATHML_DICT.items():
        html = html.replace(key, value)

    return html

@app.route('/', methods=['GET','POST'])
def solver() -> str:
    '''


    Returns
    -------
    str
        The HTML of the webpage, including the form and results generated.

    '''

    if request.method == 'GET':
        return render_template('solver.html')
    try:
        a = float(request.form.get('a'))
        p = float(request.form.get('p'))
        px = float(request.form.get('px'))
        py = float(request.form.get('py'))
        m = float(request.form.get('m'))

        input_ = f"""You entered the parameters
                    'a'={a},
                    'p'={p},
                    'px'={px},
                    'py'={py},
                    and
                    'm'={m}."""
        input_ = convert_to_mathml(input_)


    except ValueError:
        solution = "Entries must be numbers."
        return render_template('solver.html',
                               solution=solution,
                               )

    try:
        CP = ConsumerProblem(a=a, p=p, px=px, py=py, m=m)

        try:
            optimal_bundle = CP.tangency()
            x, y = symbols('x y')
            x_opt, y_opt = optimal_bundle[x], optimal_bundle[y]
            solution = f"""The consumer buys {x_opt:.2f} units of Good X and
                        {y_opt:.2f} units of Good Y."""
            fig = CP.plot()
            buf = BytesIO()
            fig.savefig(buf, format="png")
            data = base64.b64encode(buf.getbuffer()).decode("ascii")
            img = f"<img src='data:image/png;base64,{data}'/>"

        except (IndexError, KeyError):
            solution = """This tool is currently unable to solve the consumer
                          problem for these parameters."""
            return render_template('solver.html',
                                   solution=solution,
                                   )

    except ValueError as e:
        solution = convert_to_mathml(str(e))

        return render_template('solver.html',
                               input_=input_,
                               solution=solution,
                               )

    return render_template('solver.html',
                           input_=input_,
                           solution=solution,
                           img=img,
                           )

if __name__ == "__main__":
    app.run()