from matplotlib.figure import Figure
import numpy as np

from sympy import (
    Function,
    simplify,
    solve,
    symbols,
    )

x, y = symbols('x y')

class CES(Function):
    @classmethod
    def eval(cls,
             x: float,
             y: float,
             a: float,
             p: float,
             ) -> float:
        """


        Parameters
        ----------
        x : float
            The amount purchased of Good X.
        y : float
            The amount purchased of Good Y.
        a : float
            A parameter of the CES utility function.
        p : float
            A parameter of the CES utility function.

        Raises
        ------
        ValueError
            'a' and 'p' must be within the ranges required for CES utility.

        Returns
        -------
        float
            The utility for the given parameters and amounts purchased.

        """

        if a <= 0 or a >= 1:
            raise ValueError("'a' must be strictly between 0 and 1")
        if p > 1:
            raise ValueError("'p' must be less than or equal to 1")
        if p == 0: #Cobb-Douglas
            return x**a * y**(1-a)
        if p <= 1: #general CES
            return (a*x**p + (1-a)*y**p)**(1/p)

class ConsumerProblem:
    def __init__(self,
                 a: float,
                 p: float,
                 px: float,
                 py: float,
                 m: float,
                 ) -> None:
        """


        Parameters
        ----------
        a : float
            A parameter of the CES utility funciton.
        p : float
            A parameter of the CES utility function.
        px : float
            The price of Good X.
        py : float
            The price of Good Y.
        m : float
            The consumer's income.

        Raises
        ------
        ValueError
            The prices and income must be positive.

        Returns
        -------
        None
            Sets the attributes of the ConsumerProblem class.

        """

        if px <= 0 or py <= 0:
            raise ValueError("'px' and 'px' must be positive")
        if m <= 0:
            raise ValueError("'m' must be positive")
        self.a = a
        self.p = p
        self.px = px
        self.py = py
        self.m = m
        self.f = CES.eval(x, y, self.a, self.p)

    def utility(self, x: float, y: float) -> float:
        """


        Parameters
        ----------
        x : float
            The amount purchased of Good X.
        y : float
            The amount purchased of Good Y.

        Returns
        -------
        float
            The utility obtained from these amounts purchased.

        """
        return CES.eval(x=x, y=y, a=self.a, p=self.p)

    def indiff_curve(self, x: np.ndarray, c: float) -> np.ndarray:
        """


        Parameters
        ----------
        x : np.ndarray
            A numpy array of values for amounts purchased of Good X.
        c : float
            The utility associated with the indifference curve.

        Returns
        -------
        np.ndarray
            The y-values of the indifference curve over the given x-values,
            where they are defined.

        """
        if self.p == 0:
            return (c*x**(-self.a))**(1/(1-self.a))
        base = (c**self.p - self.a*x**self.p)/(1-self.a)
        
        return np.piecewise(base,
                            [base<=0, base>0],
                            [None, lambda base: base**(1/self.p)])

    def budget_cons(self, x: np.ndarray) -> np.ndarray:
        """


        Parameters
        ----------
        x : np.ndarray
            A numpy array of values for amounts purchased of Good X.

        Returns
        -------
        np.ndarray
            The y-values of the budget line over the given x-values.

        """
        return (self.m - self.px * x) / self.py
    
    def budget_cons_intercepts(self) -> tuple[float]:
        """
        

        Returns
        -------
        tuple[float]
            The x- and y-intercepts of the budget constraint.

        """
        x_intercept = solve((self.m - self.px * x) / self.py, x)[0]
        y_intercept = self.budget_cons(0)
        
        return x_intercept, y_intercept

    def tangency(self) -> dict:
        """


        Returns
        -------
        dict
            A dictionary associating 'x' and 'y' to their optimal values
            for this consumer problem.

        """
        try:
            optimal_bundle = solve([simplify(self.f.diff(x)/self.f.diff(y))
                                    - self.px/self.py, 
                                    self.px*x + self.py*y - self.m
                                    ],
                                   (x, y), dict=True)[0]
        except IndexError:
            #no point of tangency
            x_intercept, y_intercept = self.budget_cons_intercepts()
            x_utility = self.utility(x=x_intercept, y=0)
            y_utility = self.utility(x=0, y=y_intercept)
            if x_utility > y_utility:
                optimal_bundle = {x: x_intercept, y: 0}
            else:
                optimal_bundle = {x: 0, y: y_intercept}
   
        if y not in optimal_bundle:
            raise NotImplementedError("All points on budget line are optimal.")
            
        return optimal_bundle

    def plot(self) -> Figure:
        """


        Returns
        -------
        Figure
            A figure plotting the solution of the consumer problem.
            The indifference curve that is tangent to the budget line
            is plotted, along with two indifference curves below and two above.
            Axes limits are set so that the slope of the budget line is clear.

        """
        x_intercept, y_intercept = self.budget_cons_intercepts()
        lim_x, lim_y = 1.1 * x_intercept, 1.1 * y_intercept
        lim = max(float(lim_y), float(lim_x))
        
        try:
            optimal_bundle = self.tangency()
            x_opt, y_opt = float(optimal_bundle[x]), float(optimal_bundle[y])
        except NotImplementedError:
            x_opt, y_opt = x_intercept / 2, y_intercept / 2
        
        opt_util = self.utility(x=x_opt, y=y_opt)
        c_list = [
            (1/3)*opt_util,
            (2/3)*opt_util,
            opt_util,
            (4/3)*opt_util,
            (5/3)*opt_util,
            ]
        x_vals = np.linspace(1e-10, lim, 1_000)
        fig = Figure()
        fig.suptitle("Consumer Problem with CES Utility")
        ax = fig.add_axes(
            rect=(0.1, 0.1, 0.8, 0.8), 
            xlim=(0, lim), 
            ylim=(0, lim),
            xlabel="Quantity of Good X",
            ylabel="Quantity of Good Y",
            )
        
        for c in c_list:
            ax.plot(x_vals, self.indiff_curve(x_vals, c), color='orange')
        ax.plot(x_vals, self.budget_cons(x_vals), color='blue')
        
        return fig