import plotly.graph_objects as go

from plotly.offline import plot
from econtools.budget import Budget
from econtools.utility import CobbDouglas


class Slutsky:
    """
    Implementation of the Slutsky equation, accepts two budgets, a utility function, and calculates
    the income and substitution effects
    """
    def __init__(
            self,
            old_budget: Budget,
            new_budget: Budget,
            utility_function: CobbDouglas  # need to replace with utility superclass
    ):
        self.name = 'Slutsky'
        self.old_budget = old_budget
        self.old_budget.name = 'Old Budget'
        self.new_budget = new_budget
        self.new_budget.name = 'New Budget'
        self.utility = utility_function
        self.endowment_mode = self.__toggle_endowment()

        self.old_bundle = self.utility.optimal_bundle(
            self.old_budget.good_x.price,
            self.old_budget.good_y.price,
            self.old_budget.income
        )

        self.delta_p = self.new_budget.good_x.price - self.old_budget.good_x.price
        self.pivoted_budget = self.calculate_pivoted_budget()
        self.substitution_bundle = self.calculate_substitution_bundle()
        self.substitution_effect = self.calculate_substitution_effect()
        self.ordinary_income_budget = self.calculate_ordinary_income_budget()
        self.income_bundle = self.calculate_ordinary_income_bundle()
        self.income_effect = self.calculate_income_effect()
        self.endowment_income_bundle = self.calculate_endowment_income_bundle()
        self.endowment_income_effect = self.calculate_endowment_income_effect()
        self.total_effect = self.substitution_effect + self.income_effect
        self.substitution_rate = self.calculate_substitution_rate()
        self.income_rate = self.calculate_income_rate()
        self.slutsky_rate = self.substitution_rate - self.income_rate
        self.plot = self.get_plot()

    def __toggle_endowment(self):
        """
        Detect whether endowment is present
        """
        if (self.old_budget.endowment is not None) and (self.new_budget.endowment is not None):
            return True
        else:
            return False

    def calculate_pivoted_budget(self):
        """
        Pivot the budget line at the new price so the consumer can still afford their old bundle
        """
        delta_m = self.old_bundle[0] * self.delta_p
        pivoted_income = self.old_budget.income + delta_m
        pivoted_budget = Budget(
            self.new_budget.good_x,
            self.old_budget.good_y,
            pivoted_income,
            'Pivoted Budget'
        )
        return pivoted_budget

    def calculate_substitution_bundle(self):
        """
        Return the bundle consumed after pivoting the budget line
        """
        substitution_bundle = self.utility.optimal_bundle(
            self.pivoted_budget.good_x.price,
            self.pivoted_budget.good_y.price,
            self.pivoted_budget.income
        )
        return substitution_bundle

    def calculate_substitution_effect(self):
        substitution_effect = self.substitution_bundle[0] - self.old_bundle[0]
        return substitution_effect

    def calculate_ordinary_income_budget(self):
        ordinary_income_budget = Budget(
            good_x=self.new_budget.good_x,
            good_y=self.new_budget.good_y,
            income=self.old_budget.income,
            name='Ordinary Income Budget')

        return ordinary_income_budget

    def calculate_ordinary_income_bundle(self):
        """
        Shift the budget line outward
        """
        # if endowment present, fix income at old income
        if self.endowment_mode:
            income = self.old_budget.income
        else:
            income = self.new_budget.income

        income_bundle = self.utility.optimal_bundle(
            self.new_budget.good_x.price,
            self.new_budget.good_y.price,
            income
        )
        return income_bundle

    def calculate_income_effect(self):
        income_effect = self.income_bundle[0] - self.substitution_bundle[0]
        return income_effect

    def calculate_endowment_income_bundle(self):
        # only works if both old and new budget were defined with an endowment
        if self.endowment_mode:
            endowment_income_bundle = self.utility.optimal_bundle(
                self.new_budget.good_x.price,
                self.new_budget.good_y.price,
                self.new_budget.income
            )
            return endowment_income_bundle
        else:
            return None

    def calculate_endowment_income_effect(self):

        # only works if both old and new budget were defined with an endowment
        if self.endowment_mode:
            endowment_income_effect = self.endowment_income_bundle[0] - self.income_bundle[0]
            return endowment_income_effect
        else:
            return 0

    def calculate_substitution_rate(self):
        delta_s = self.calculate_substitution_effect()
        delta_p = self.new_budget.good_x.price - self.old_budget.good_x.price
        substitution_rate = delta_s / delta_p
        return substitution_rate

    def calculate_income_rate(self):
        delta_p = self.new_budget.good_x.price - self.old_budget.good_x.price
        delta_m = self.old_bundle[0] * delta_p
        delta_x1m = -self.calculate_income_effect()
        income_rate = delta_x1m / delta_m * self.old_bundle[0]
        return income_rate

    def get_plot(self):
        max_x_int = max(
            self.old_budget.income / self.old_budget.good_x.price,
            self.old_budget.income / self.new_budget.good_x.price,
            self.pivoted_budget.income / self.pivoted_budget.good_x.price,
            self.new_budget.income / self.new_budget.good_x.price
        ) * 1.2

        max_y_int = max(
            self.old_budget.income,
            self.pivoted_budget.income,
            self.new_budget.income,
        ) * 1.2

        # interval boundaries
        effect_boundaries = [
            self.income_bundle[0],
            self.substitution_bundle[0],
            self.old_bundle[0],
            self.endowment_income_bundle[0] if self.endowment_mode else None
        ]
        effect_boundaries = list(filter(None.__ne__, effect_boundaries))
        effect_boundaries.sort()

        fig = go.Figure()

        # budget lines
        fig.add_trace(self.old_budget.get_line())
        fig.add_trace(self.pivoted_budget.get_line())
        fig.add_trace(self.new_budget.get_line())
        if self.endowment_mode:
            fig.add_trace(self.ordinary_income_budget.get_line())

        # utility curves
        fig.add_trace(
            self.utility.trace(
                k=self.old_bundle[2],
                m=max_x_int,
                name='Old Utility'
            )
        )
        fig.add_trace(
            self.utility.trace(
                k=self.substitution_bundle[2],
                m=max_x_int,
                name='Pivoted Utility'
            )
        )
        fig.add_trace(
            self.utility.trace(
                k=self.income_bundle[2],
                m=max_x_int,
                name='Ordinary Income Utility' if self.endowment_mode else 'New Utility'
            )
        )
        if self.endowment_mode:
            fig.add_trace(
                self.utility.trace(
                    k=self.endowment_income_bundle[2],
                    m=max_x_int,
                    name='New Utility'
                )
            )
        # consumption bundles

        fig.add_trace(
            go.Scatter(
                x=[self.old_bundle[0]],
                y=[self.old_bundle[1]],
                mode='markers+text',
                text=['Old Bundle'],
                textposition='top center',
                marker=dict(
                    size=[15],
                    color=[1]
                ),
                showlegend=False
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[self.substitution_bundle[0]],
                y=[self.substitution_bundle[1]],
                mode='markers+text',
                text=['Pivoted Bundle'],
                textposition='top center',
                marker=dict(
                    size=[15],
                    color=[2]
                ),
                showlegend=False
            )
        )

        fig.add_trace(
            go.Scatter(
                x=[self.income_bundle[0]],
                y=[self.income_bundle[1]],
                mode='markers+text',
                text=['Ordinary Income Bundle' if self.endowment_mode else 'New Bundle'],
                textposition='top center',
                marker=dict(
                    size=[15],
                    color=[3]
                ),
                showlegend=False
            )
        )
        if self.endowment_mode:
            fig.add_trace(
                go.Scatter(
                    x=[self.endowment_income_bundle[0]],
                    y=[self.endowment_income_bundle[1]],
                    mode='markers+text',
                    text=['New Bundle'],
                    textposition='top center',
                    marker=dict(
                        size=[15],
                        color=[3]
                    ),
                    showlegend=False
                )
            )

        # Substitution and income effect interval lines
        fig.add_shape(
            type='line',
            x0=self.substitution_bundle[0],
            y0=self.substitution_bundle[1],
            x1=self.substitution_bundle[0],
            y1=0,
            line=dict(
                color="grey",
                dash="dashdot",
                width=1
            )
        )

        fig.add_shape(
            type='line',
            x0=self.income_bundle[0],
            y0=self.income_bundle[1],
            x1=self.income_bundle[0],
            y1=0,
            line=dict(
                color="grey",
                dash="dashdot",
                width=1
            )
        )

        fig.add_shape(
            type='line',
            x0=self.old_bundle[0],
            y0=self.old_bundle[1],
            x1=self.old_bundle[0],
            y1=0,
            line=dict(
                color="grey",
                dash="dashdot",
                width=1
            )
        )

        if self.endowment_mode:
            fig.add_shape(
                type='line',
                x0=self.endowment_income_bundle[0],
                y0=self.endowment_income_bundle[1],
                x1=self.endowment_income_bundle[0],
                y1=0,
                line=dict(
                    color="grey",
                    dash="dashdot",
                    width=1
                )
            )

        fig.add_shape(
            type='line',
            xref='x',
            yref='y',
            x0=effect_boundaries[0],
            y0=max_y_int / 10,
            x1=effect_boundaries[1],
            y1=max_y_int / 10,
            line=dict(
                color='grey',
                dash='dashdot'
            )
        )
        fig.add_shape(
            type='line',
            xref='x',
            yref='y',
            x0=effect_boundaries[1],
            y0=max_y_int / 15,
            x1=effect_boundaries[2],
            y1=max_y_int / 15,
            line=dict(
                color='grey',
                dash='dashdot'
            )
        )

        if self.endowment_mode:
            fig.add_shape(
                type='line',
                xref='x',
                yref='y',
                x0=effect_boundaries[2],
                y0=max_y_int / 15,
                x1=effect_boundaries[3],
                y1=max_y_int / 15,
                line=dict(
                    color='grey',
                    dash='dashdot'
                )
            )

        fig.add_shape(
            type='line',
            xref='x',
            yref='y',
            x0=effect_boundaries[0],
            y0=max_y_int / 20,
            x1=effect_boundaries[-1],
            y1=max_y_int / 20,
            line=dict(
                color='grey',
                dash='dashdot'
            )
        )

        fig.add_annotation(
            x=(self.substitution_bundle[0] + self.old_bundle[0]) / 2,
            y=max_y_int / 10,
            text='Substitution<br />Effect',
            xref='x',
            yref='y',
            showarrow=True,
            arrowhead=7,
            ax=5,
            ay=-40,
        )

        fig.add_annotation(
            x=(self.income_bundle[0] + self.substitution_bundle[0]) / 2,
            y=max_y_int / 15,
            text='Ordinary Income Effect',
            xref='x',
            yref='y',
            showarrow=True,
            arrowhead=7,
            ax=50,
            ay=-20
        )

        if self.endowment_mode:
            fig.add_annotation(
                x=(self.income_bundle[0] + self.endowment_income_bundle[0]) / 2,
                y=max_y_int / 15,
                text='Endowment Income Effect',
                xref='x',
                yref='y',
                showarrow=True,
                arrowhead=7,
                ax=50,
                ay=-20
            )

        fig.add_annotation(
            x=(effect_boundaries[-1] + effect_boundaries[0]) / 2,
            y=max_y_int / 20,
            text='Total Effect',
            xref='x',
            yref='y',
            showarrow=True,
            arrowhead=7,
            ax=100,
            ay=20
        )

        fig['layout'].update({
            'title': self.name + ' Decomposition',
            'title_x': 0.5,
            'xaxis': {
                'title': 'Amount of Insurance',
                'range': [0, max_x_int]
            },
            'yaxis': {
                'title': 'Amount of All Other Goods',
                'range': [0, max_y_int]
            }
        })
        return fig

    def show_plot(self):
        plot(self.plot)
