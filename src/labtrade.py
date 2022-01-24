# LabTrade - A visual tool to support the development of strategies in Quantitative Finance - by fab2112
import sys
import numpy as np
import pandas as pd
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui


class labtrade:
    def __init__(self):
        # Variables Logic
        self.showplt1 = 1  # Performance / Signals
        self.showplt2 = 1  # Positions & Signals
        self.showplt3 = 1  # Features
        self.showplt4 = 1  # Cumulative Amount
        self.showplt5 = 1  # Equity Curve Scatter
        self.cumulative_amount_curve_str = 0
        self.equity_curve_true = 0
        self.equity_curve_pred = 0
        self.logic = None
        self.amount = None
        self.pct_rate = None

        self.frame_plot = pg.GraphicsLayoutWidget(title="LabTrade v1.0.0")
        self.frame_plot.setGeometry(150, 100, 1400, 900)
        self.frame_plot.setBackground(background='#1E1E1E')

        # ">" - Performance
        self.button_1 = QtGui.QPushButton(self.frame_plot)
        self.button_1.clicked.connect(self.show_plot)
        self.button_1.setGeometry(10, 10, 20, 20)
        self.button_1.setText('>')
        self.button_1.show()
        self.button_1.setStyleSheet("font: bold 11pt ;color: white; background-color: #483D8B; "
                                    "border-radius: 1px; border: 1px solid grey")

        # "-" - Signals / Positions / Pct-change
        self.button_2 = QtGui.QPushButton(self.frame_plot)
        self.button_2.clicked.connect(self.show_signals_positions)
        self.button_2.setGeometry(40, 10, 20, 20)
        self.button_2.setText('-')
        self.button_2.setStyleSheet("font: bold 11pt ;color: white; background-color: #483D8B; "
                                    "border-radius: 1px; border: 1px solid grey")

        # "X" - Features
        self.button_3 = QtGui.QPushButton(self.frame_plot)
        self.button_3.clicked.connect(self.show_features)
        self.button_3.setGeometry(70, 10, 20, 20)
        self.button_3.setText('X')
        self.button_3.setStyleSheet("font: bold 11pt ;color: white; background-color: #483D8B; "
                                    "border-radius: 1px; border: 1px solid grey")

        # "A" - Cumulative Amount
        self.button_4 = QtGui.QPushButton(self.frame_plot)
        self.button_4.clicked.connect(self.show_cumulative_amount)
        self.button_4.setGeometry(100, 10, 20, 20)
        self.button_4.setText('A')
        self.button_4.setStyleSheet("font: bold 11pt ;color: white; background-color: #483D8B; "
                                    "border-radius: 1px; border: 1px solid grey")

        self.plt_1 = self.frame_plot.addPlot(row=0, col=1)
        self.plt_2 = self.frame_plot.addPlot(row=1, col=1)
        self.plt_3 = self.frame_plot.addPlot(row=2, col=1)

        self.font = QtGui.QFont("TypeWriter")
        self.font.setPixelSize(13)

        # Risk Metrics
        self.risk_metrics_textitem = pg.TextItem(color="#8FBC8F")
        self.risk_metrics_textitem.setParentItem(self.plt_3)
        self.risk_metrics_textitem.setPos(10, 5)
        self.risk_metrics_textitem.setFont(self.font)

        # Profit and Losses
        self.pnl_textitem = pg.TextItem(color="#5EF38C")
        self.pnl_textitem.setParentItem(self.plt_2)
        self.pnl_textitem.setPos(10, 5)
        self.pnl_textitem.setFont(self.font)

        # Drawndown
        self.drawdown_textitem = pg.TextItem(color="#ff3562")
        self.drawdown_textitem.setParentItem(self.plt_2)
        self.drawdown_textitem.setPos(125, 5)
        self.drawdown_textitem.setFont(self.font)

        self.qGraphicsGridLayout = self.frame_plot.ci.layout
        self.qGraphicsGridLayout.setRowStretchFactor(0, 1)
        self.qGraphicsGridLayout.setRowStretchFactor(1, 1)
        self.qGraphicsGridLayout.setRowStretchFactor(2, 1)

        self.plt_1.showGrid(x=True, y=True, alpha=0.3)
        self.plt_2.showGrid(x=True, y=True, alpha=0.3)
        self.plt_3.showGrid(x=True, y=True, alpha=0.3)
        self.plt_1.hideAxis('left')
        self.plt_1.showAxis('right')
        self.plt_2.hideAxis('left')
        self.plt_2.showAxis('right')
        self.plt_3.hideAxis('left')
        self.plt_3.showAxis('right')
        self.plt_1.setXLink(self.plt_3)
        self.plt_2.setXLink(self.plt_3)
        self.plt_1.getAxis('bottom').setStyle(showValues=False)
        self.plt_2.getAxis('bottom').setStyle(showValues=False)

    def plot(self, df_1=None, pos_true=None, pos_pred=None, pct_rate=None, stop_rate=np.inf, gain_rate=np.inf,
             logic='long-short', amount=0, maker_fee=None, risk_free=1, period=365):

        self.logic = logic
        self.amount = amount
        self.pct_rate = pct_rate
        self.maker_fee = maker_fee
        self.risk_free = risk_free
        self.period = period

        proxy = pg.SignalProxy(self.frame_plot.scene().sigMouseMoved, rateLimit=60, slot=self.mouse_event)

        self.df_1 = self.iter_df(df_1, pos_true, pos_pred, pct_rate, stop_rate, gain_rate, logic, amount)

        self.x_line_plt1 = pg.InfiniteLine(angle=90, movable=False, pen={'color': '#969696', 'width': 0.5},
                                           label='{value:0.1f}', labelOpts={'position': 0.05, 'color': '#D3D3D3',
                                                                            'movable': True})
        self.y_line_plt1 = pg.InfiniteLine(angle=0, movable=False, pen={'color': '#969696', 'width': 0.5},
                                           label='{value:0.1f}', labelOpts={'position': 0.97, 'color': '#D3D3D3',
                                                                            'movable': True})

        self.x_line_plt2 = pg.InfiniteLine(angle=90, movable=False, pen={'color': '#969696', 'width': 0.5},
                                           label='{value:0.1f}', labelOpts={'position': 0.96, 'color': '#D3D3D3',
                                                                            'movable': True})
        self.y_line_plt2 = pg.InfiniteLine(angle=0, movable=False, pen={'color': '#969696', 'width': 0.5},
                                           label='{value:0.1f}', labelOpts={'position': 0.03, 'color': '#D3D3D3',
                                                                            'movable': True})

        self.x_line_plt3 = pg.InfiniteLine(angle=90, movable=False, pen={'color': '#969696', 'width': 0.5},
                                           label='{value:0.1f}', labelOpts={'position': 0.96, 'color': '#D3D3D3',
                                                                            'movable': True})
        self.y_line_plt3 = pg.InfiniteLine(angle=0, movable=False, pen={'color': '#969696', 'width': 0.5},
                                           label='{value:0.1f}', labelOpts={'position': 0.03, 'color': '#D3D3D3',
                                                                            'movable': True})
        self.show_plot()

        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def show_plot(self):

        self.risk_metrics_textitem.hide()
        self.pnl_textitem.hide()
        self.drawdown_textitem.hide()

        self.qGraphicsGridLayout.setRowStretchFactor(0, 1)
        self.qGraphicsGridLayout.setRowStretchFactor(1, 1)
        self.qGraphicsGridLayout.setRowStretchFactor(2, 1)

        self.showplt3 = 1

        # Show Signals
        if self.showplt1 == 1:
            self.show_scatter(self.df_1)
            self.button_2.show()
            self.button_4.hide()
            self.plt_1.clear()
            self.plt_2.clear()
            self.plt_3.clear()

            # Scatter plot y_true
            self.plt_1.setTitle('y-true signals')
            self.plt_1.plot(self.df_1.c)
            self.plt_1.addItem(self.scatter_long_true)
            self.plt_1.addItem(self.scatter_short_true)
            if self.logic == "long-short-exit":
                self.plt_1.addItem(self.scatter_exit_true_long)
                self.plt_1.addItem(self.scatter_exit_true_short)
            self.plt_1.addItem(self.scatter_exit_gain_true)
            self.plt_1.addItem(self.scatter_exit_stop_true)

            # Scatter plot y_pred
            self.plt_2.setTitle('y-pred signals')
            self.plt_2.plot(self.df_1.c)
            self.plt_2.addItem(self.scatter_long_pred)
            self.plt_2.addItem(self.scatter_short_pred)
            if self.logic == "long-short-exit":
                self.plt_2.addItem(self.scatter_exit_pred_long)
                self.plt_2.addItem(self.scatter_exit_pred_short)
            self.plt_2.addItem(self.scatter_exit_gain_pred)
            self.plt_2.addItem(self.scatter_exit_stop_pred)

            # y_true x y_pred
            self.plt_3.setTitle('y_true positions (green)   |   y_pred positions (red)')
            self.plt_3.plot(self.df_1.positions_true * self.amount, pen={'color': (127, 200, 0), 'width': 0.6})  # GREEN
            self.plt_3.plot(self.df_1.positions_pred * self.amount, pen={'color': (255, 20, 30)})
            self.showplt1 = 2
            self.showplt2 = 2

        # Show Performance
        else:
            self.button_2.hide()
            self.button_4.show()
            self.plt_1.clear()
            self.plt_2.clear()
            self.plt_3.clear()

            # Returns pct
            self.returns = self.df_1.c.pct_change()

            # Returns log
            # self.returns = np.log(self.df_1.c / self.df_1.c.shift(1))

            # Strategy returns
            self.strategy_returns_pred = (self.returns * self.df_1.positions_pred.shift(1)).fillna(0)
            self.strategy_returns_true = (self.returns * self.df_1.positions_true.shift(1)).fillna(0)

            if self.maker_fee is not None:
                self.strategy_returns_pred = self.apply_tax(
                    self.df_1.positions_pred, self.strategy_returns_pred, self.maker_fee)

            # Amount vetorial
            self.df_1.amount_hold = ((1 + self.returns).cumprod() * self.amount).fillna(self.amount)
            self.df_1.amount_str = ((1 + self.strategy_returns_pred).cumprod() * self.amount).fillna(self.amount)
            self.cumulative_amount_curve_hold = self.df_1.amount_hold
            self.cumulative_amount_curve_str = self.df_1.amount_str

            # Returns cumalative (Strategy x Market)
            self.market_returns_cum = (self.returns.cumsum()).fillna(method='bfill')
            self.strategy_returns_cum = (self.strategy_returns_pred.cumsum()).fillna(method='bfill')

            text = 'PNL: ' + str("%.2f" % (self.strategy_returns_cum.values[-1] * 100)) + "%"
            if self.strategy_returns_cum.values[-1] > 0:
                self.pnl_textitem.setText(text=text, color="#5EF38C")
            else:
                self.pnl_textitem.setText(text=text, color="#7D7ABC")
            self.pnl_textitem.show()

            self.plt_2.setTitle('Strategy (Green)  |  Hold (Grey)')
            self.plt_2.plot(self.market_returns_cum, pen={'color': '#A9A9A9', 'width': 0.3})
            self.plt_2.plot(self.strategy_returns_cum, pen={'color': 'g', 'width': 0.7})
            self.plt_2.addLine(x=None, y=0, pen={'color': '#969696', 'width': 0.4})

            # Equity Curve
            self.equity_curve_true = ((self.strategy_returns_true.cumsum()) + 1)
            self.equity_curve_pred = ((self.strategy_returns_pred.cumsum()) + 1)
            # self.equity_curve_pred = np.cumprod(1 + self.strategy_returns_pred.values)
            self.plt_3.setTitle('Equity Curve y-pred (Blue)  |  y-true (Green)')
            self.plt_3.plot(self.equity_curve_pred, pen={'color': '#63B8FF', 'width': 0.7})
            self.plt_3.plot(self.equity_curve_true, pen={'color': 'g', 'width': 0.2})

            # Scatter plot y_pred
            self.showplt5 = 2
            self.showplt4 = 1
            self.show_scatter(self.df_1)
            self.plt_3.addItem(self.scatter_long_pred)
            self.plt_3.addItem(self.scatter_short_pred)

            if self.logic == "long-short-exit":
                self.plt_3.addItem(self.scatter_exit_pred_long)
                self.plt_3.addItem(self.scatter_exit_pred_short)
            self.plt_3.addItem(self.scatter_exit_gain_pred)
            self.plt_3.addItem(self.scatter_exit_stop_pred)

            self.showplt1 = 1

            # Drawdowns
            self.drawdown = self.drawdowns(pd.Series(self.equity_curve_pred))
            self.grad = QtGui.QLinearGradient(0, 0, 0, -1)
            self.grad.setColorAt(0.15, pg.mkColor('#27408B'))
            self.grad.setColorAt(0.4, pg.mkColor('#CD0000'))
            self.brush = QtGui.QBrush(self.grad)
            self.plt_1.setTitle('Drawndown')
            self.plt_1.setYRange(0.0, - 0.4)
            self.plt_1.plot(self.drawdown[0], pen={'color': '#1E1E1E', 'width': 1.0}, fillBrush=self.brush, fillLevel=0)
            self.plt_1.addLine(x=None, y=0, pen={'color': '#27408B', 'width': 0.8})
            self.plt_1.enableAutoRange('y', True)

            text = 'DD-MAX: ' + str("%.2f" % (self.drawdown[0].min() * 100)) + "%" + \
                   '     DD-DURATION: ' + str(int(self.drawdown[1].max()))
            self.drawdown_textitem.setText(text=text, color="#ff3562")
            self.drawdown_textitem.show()

            # Risk Metrics
            self.show_risk_metrics(self.period, self.risk_free)

        self.plt_1.addItem(self.x_line_plt1, ignoreBounds=True)
        self.plt_1.addItem(self.y_line_plt1, ignoreBounds=True)
        self.plt_2.addItem(self.x_line_plt2, ignoreBounds=True)
        self.plt_2.addItem(self.y_line_plt2, ignoreBounds=True)
        self.plt_3.addItem(self.x_line_plt3, ignoreBounds=True)
        self.plt_3.addItem(self.y_line_plt3, ignoreBounds=True)

        self.plt_1.enableAutoRange()
        self.plt_2.enableAutoRange()
        self.plt_3.enableAutoRange()

        self.frame_plot.show()

    def show_signals_positions(self):

        self.risk_metrics_textitem.hide()
        self.pnl_textitem.hide()
        self.drawdown_textitem.hide()

        if self.showplt3 == 1:

            if self.showplt2 == 1:
                self.plt_3.clear()
                self.plt_3.setTitle('y_true positions (green)   |   y_pred positions (red)')
                self.plt_3.plot(self.df_1.positions_true * self.amount, pen={'color': (127, 200, 0), 'width': 0.6})
                self.plt_3.plot(self.df_1.positions_pred * self.amount, pen={'color': (255, 20, 30)})
                self.showplt2 = 2

            elif self.showplt2 == 2:
                self.plt_3.clear()
                self.plt_3.setTitle('y_true signals (green)   |   y_pred signals (red)')
                self.plt_3.plot(self.df_1.signals_true, pen={'color': (127, 200, 0), 'width': 0.6})  # GREEN
                self.plt_3.plot(self.df_1.signals_pred, pen={'color': (255, 20, 30)})
                self.showplt2 = 3

            elif self.showplt2 == 3:
                self.plt_3.clear()
                self.plt_3.setTitle('y_true signals_size (green)   |   y_pred signals_size (red)')
                self.plt_3.plot(self.df_1.signals_size_true, pen={'color': (127, 200, 0), 'width': 0.6})  # GREEN
                self.plt_3.plot(self.df_1.signals_size_pred, pen={'color': (255, 20, 30)})
                self.showplt2 = 4

            else:
                if self.pct_rate:
                    self.plt_3.clear()
                    self.plt_3.setTitle('y_true percentage_rate (green)   |   y_pred percentage_rate (red)')
                    self.plt_3.plot(self.df_1.true, pen={'color': (127, 200, 0), 'width': 0.6})  # GREEN
                    self.plt_3.plot(self.df_1.pred, pen={'color': (255, 20, 30)})
                    self.showplt2 = 1

                else:
                    self.plt_3.clear()
                    self.plt_3.setTitle('y_true positions (green)   |   y_pred positions (red)')
                    self.plt_3.plot(self.df_1.positions_true * self.amount, pen={'color': (127, 200, 0), 'width': 0.6})
                    self.plt_3.plot(self.df_1.positions_pred * self.amount, pen={'color': (255, 20, 30)})
                    self.showplt2 = 2

            self.plt_3.addItem(self.x_line_plt3, ignoreBounds=True)
            self.plt_3.addItem(self.y_line_plt3, ignoreBounds=True)

        self.plt_1.enableAutoRange()
        self.plt_2.enableAutoRange()
        self.plt_3.enableAutoRange()

    def show_features(self):

        self.risk_metrics_textitem.hide()
        self.pnl_textitem.hide()
        self.drawdown_textitem.hide()
        self.button_2.hide()
        self.button_4.hide()

        self.plt_1.setTitle('plot_1 - Features')
        self.plt_2.setTitle('plot_2 - Features')
        self.plt_3.setTitle('plot_3 - Features')

        self.showplt1 = 1

        self.plt_1.clear()
        self.plt_2.clear()
        self.plt_3.clear()

        self.plt_1.addItem(self.x_line_plt1, ignoreBounds=True)
        self.plt_1.addItem(self.y_line_plt1, ignoreBounds=True)
        self.plt_2.addItem(self.x_line_plt2, ignoreBounds=True)
        self.plt_2.addItem(self.y_line_plt2, ignoreBounds=True)
        self.plt_3.addItem(self.x_line_plt3, ignoreBounds=True)
        self.plt_3.addItem(self.y_line_plt3, ignoreBounds=True)

        self.qGraphicsGridLayout.setRowStretchFactor(0, 1)
        self.qGraphicsGridLayout.setRowStretchFactor(1, 2)
        self.qGraphicsGridLayout.setRowStretchFactor(2, 1)

        # Plot Features
        if self.showplt3 == 1:
            # White
            self.plt_1.plot(self.df_1.filter(regex="PLT1_WHITE.*", axis=1).values.reshape(-1),
                            pen={'color': "#FFFAF0", 'width': 1})
            self.plt_2.plot(self.df_1.filter(regex="PLT2_WHITE.*", axis=1).values.reshape(-1),
                            pen={'color': "#FFFAF0", 'width': 1})
            self.plt_3.plot(self.df_1.filter(regex="PLT3_WHITE.*", axis=1).values.reshape(-1),
                            pen={'color': "#FFFAF0", 'width': 1})

            # Blue
            self.plt_1.plot(self.df_1.filter(regex="PLT1_BLUE.*", axis=1).values.reshape(-1),
                            pen={'color': "#3399FF", 'width': 1})
            self.plt_2.plot(self.df_1.filter(regex="PLT2_BLUE.*", axis=1).values.reshape(-1),
                            pen={'color': "#3399FF", 'width': 1})
            self.plt_3.plot(self.df_1.filter(regex="PLT3_BLUE.*", axis=1).values.reshape(-1),
                            pen={'color': "#3399FF", 'width': 1})

            # Red
            self.plt_1.plot(self.df_1.filter(regex="PLT1_RED.*", axis=1).values.reshape(-1),
                            pen={'color': "#FF3333", 'width': 1})
            self.plt_2.plot(self.df_1.filter(regex="PLT2_RED.*", axis=1).values.reshape(-1),
                            pen={'color': "#FF3333", 'width': 1})
            self.plt_3.plot(self.df_1.filter(regex="PLT3_RED.*", axis=1).values.reshape(-1),
                            pen={'color': "#FF3333", 'width': 1})

            # Yellow
            self.plt_1.plot(self.df_1.filter(regex="PLT1_YELLOW.*", axis=1).values.reshape(-1),
                            pen={'color': "#FFFF00", 'width': 1})
            self.plt_2.plot(self.df_1.filter(regex="PLT2_YELLOW.*", axis=1).values.reshape(-1),
                            pen={'color': "#FFFF00", 'width': 1})
            self.plt_3.plot(self.df_1.filter(regex="PLT3_YELLOW.*", axis=1).values.reshape(-1),
                            pen={'color': "#FFFF00", 'width': 1})

            # Orange
            self.plt_1.plot(self.df_1.filter(regex="PLT1_ORANGE.*", axis=1).values.reshape(-1),
                            pen={'color': "#FF8000", 'width': 1})
            self.plt_2.plot(self.df_1.filter(regex="PLT2_ORANGE.*", axis=1).values.reshape(-1),
                            pen={'color': "#FF8000", 'width': 1})
            self.plt_3.plot(self.df_1.filter(regex="PLT3_ORANGE.*", axis=1).values.reshape(-1),
                            pen={'color': "#FF8000", 'width': 1})

            # Green
            self.plt_1.plot(self.df_1.filter(regex="PLT1_GREEN.*", axis=1).values.reshape(-1),
                            pen={'color': "#00994C", 'width': 1})
            self.plt_2.plot(self.df_1.filter(regex="PLT2_GREEN.*", axis=1).values.reshape(-1),
                            pen={'color': "#00994C", 'width': 1})
            self.plt_3.plot(self.df_1.filter(regex="PLT3_GREEN.*", axis=1).values.reshape(-1),
                            pen={'color': "#00994C", 'width': 1})

            # Magenta
            self.plt_1.plot(self.df_1.filter(regex="PLT1_MAGENTA.*", axis=1).values.reshape(-1),
                            pen={'color': "#FF00FF", 'width': 1})
            self.plt_2.plot(self.df_1.filter(regex="PLT2_MAGENTA.*", axis=1).values.reshape(-1),
                            pen={'color': "#FF00FF", 'width': 1})
            self.plt_3.plot(self.df_1.filter(regex="PLT3_MAGENTA.*", axis=1).values.reshape(-1),
                            pen={'color': "#FF00FF", 'width': 1})

            # Cyan
            self.plt_1.plot(self.df_1.filter(regex="PLT1_CYAN.*", axis=1).values.reshape(-1),
                            pen={'color': "#00FFFF", 'width': 1})
            self.plt_2.plot(self.df_1.filter(regex="PLT2_CYAN.*", axis=1).values.reshape(-1),
                            pen={'color': "#00FFFF", 'width': 1})
            self.plt_3.plot(self.df_1.filter(regex="PLT3_CYAN.*", axis=1).values.reshape(-1),
                            pen={'color': "#00FFFF", 'width': 1})

            # Scatter plot y_pred
            self.show_scatter(self.df_1)
            self.plt_2.plot(self.df_1.c)
            self.plt_2.addItem(self.scatter_long_pred)
            self.plt_2.addItem(self.scatter_short_pred)
            if self.logic == "long-short-exit":
                self.plt_2.addItem(self.scatter_exit_pred_long)
                self.plt_2.addItem(self.scatter_exit_pred_short)
            self.plt_2.addItem(self.scatter_exit_gain_pred)
            self.plt_2.addItem(self.scatter_exit_stop_pred)

            self.plt_1.show()
            self.plt_2.show()
            self.plt_3.show()

            self.showplt3 = 2

        elif self.showplt3 == 2:
            self.showplt3 = 1
            self.show_plot()

        self.plt_1.enableAutoRange()
        self.plt_2.enableAutoRange()
        self.plt_3.enableAutoRange()

    def show_cumulative_amount(self):

        self.plt_3.clear()

        if self.showplt4 == 1:
            # Cumulative Amount  Curve
            self.plt_3.setTitle('Cumulative Amount Strategy (Orange)  X  Hold (Grey)')
            self.plt_3.plot(self.cumulative_amount_curve_str, pen={'color': '#FF9933', 'width': 0.7})
            self.plt_3.plot(self.cumulative_amount_curve_hold, pen={'color': '#A9A9A9', 'width': 0.3})

            # Scatter plot y_pred
            self.showplt5 = 2
            self.showplt4 = 2
            self.show_scatter(self.df_1)
            self.plt_3.addItem(self.scatter_long_pred)
            self.plt_3.addItem(self.scatter_short_pred)

            if self.logic == "long-short-exit":
                self.plt_3.addItem(self.scatter_exit_pred_long)
                self.plt_3.addItem(self.scatter_exit_pred_short)
            self.plt_3.addItem(self.scatter_exit_gain_pred)
            self.plt_3.addItem(self.scatter_exit_stop_pred)

        else:
            # Equity Curve
            self.plt_3.setTitle('Equity Curve y-pred (Blue)  |  y-true (Green)')
            self.plt_3.plot(self.equity_curve_pred, pen={'color': '#63B8FF', 'width': 0.7})
            self.plt_3.plot(self.equity_curve_true, pen={'color': 'g', 'width': 0.2})

            # Scatter plot y_pred
            self.showplt5 = 2
            self.showplt4 = 1
            self.show_scatter(self.df_1)
            self.plt_3.addItem(self.scatter_long_pred)
            self.plt_3.addItem(self.scatter_short_pred)

            if self.logic == "long-short-exit":
                self.plt_3.addItem(self.scatter_exit_pred_long)
                self.plt_3.addItem(self.scatter_exit_pred_short)
            self.plt_3.addItem(self.scatter_exit_gain_pred)
            self.plt_3.addItem(self.scatter_exit_stop_pred)

        self.plt_3.addItem(self.x_line_plt3, ignoreBounds=True)
        self.plt_3.addItem(self.y_line_plt3, ignoreBounds=True)

        self.plt_1.enableAutoRange()
        self.plt_2.enableAutoRange()
        self.plt_3.enableAutoRange()

    def mouse_event(self, evt):

        if self.plt_1.sceneBoundingRect().contains(evt[0]):
            mousePoint_1 = self.plt_1.vb.mapSceneToView(evt[0])
            self.x_line_plt1.setPos(mousePoint_1.x())
            self.y_line_plt1.setPos(mousePoint_1.y())
            self.x_line_plt1.show()
            self.y_line_plt1.show()
        else:
            self.x_line_plt1.hide()
            self.y_line_plt1.hide()

        if self.plt_2.sceneBoundingRect().contains(evt[0]):
            mousePoint_2 = self.plt_2.vb.mapSceneToView(evt[0])
            self.x_line_plt2.setPos(mousePoint_2.x())
            self.y_line_plt2.setPos(mousePoint_2.y())
            self.x_line_plt2.show()
            self.y_line_plt2.show()
        else:
            self.x_line_plt2.hide()
            self.y_line_plt2.hide()

        if self.plt_3.sceneBoundingRect().contains(evt[0]):
            mousePoint_3 = self.plt_3.vb.mapSceneToView(evt[0])
            self.x_line_plt3.setPos(mousePoint_3.x())
            self.y_line_plt3.setPos(mousePoint_3.y())
            self.x_line_plt3.show()
            self.y_line_plt3.show()
        else:
            self.x_line_plt3.hide()
            self.y_line_plt3.hide()

    def show_scatter(self, df_1):

        sig_ref = self.df_1.c
        size_1 = 9
        size_2 = 8
        if self.showplt5 == 2 and self.showplt4 == 1:
            self.showplt5 = 1
            sig_ref = self.equity_curve_pred
            size_1 = 4
            size_2 = 4
        elif self.showplt5 == 2 and self.showplt4 == 2:
            self.showplt5 = 1
            sig_ref = self.cumulative_amount_curve_str
            size_1 = 4
            size_2 = 4

        if self.logic == "long":
            # Scatter1 Long y_true
            self.scatter_long_true = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_true_scatter == 1],
                                                        sig_ref[self.df_1.signals_true_scatter == 1],
                                                        size=size_1, pen='#00FF7F', symbol='t1', brush='#008B00')
            # Scatter1 Exit-long y_true
            self.scatter_short_true = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_true_scatter == -2],
                                                         sig_ref[self.df_1.signals_true_scatter == -2],
                                                         size=size_1, pen='#FF0000', symbol='t', brush='#1E1E1E')
            # Scatter2 Long y_pred
            self.scatter_long_pred = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_pred_scatter == 1],
                                                        sig_ref[self.df_1.signals_pred_scatter == 1],
                                                        size=size_1, pen='#00FF7F', symbol='t1', brush='#008B00')
            # Scatter2 Exit-Long y_pred
            self.scatter_short_pred = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_pred_scatter == -2],
                                                         sig_ref[self.df_1.signals_pred_scatter == -2],
                                                         size=size_1, pen='#FF0000', symbol='t', brush='#1E1E1E')

        elif self.logic == "short":
            # Scatter1 Exit-Sort y_true
            self.scatter_long_true = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_true_scatter == 2],
                                                        sig_ref[self.df_1.signals_true_scatter == 2],
                                                        size=size_1, pen='#00FF7F', symbol='t1', brush='#1E1E1E')
            # Scatter1 Short y_true
            self.scatter_short_true = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_true_scatter == -1],
                                                         sig_ref[self.df_1.signals_true_scatter == -1],
                                                         size=size_1, pen='#FF0000', symbol='t', brush='#8B0000')
            # Scatter2 Exit-Short y_pred
            self.scatter_long_pred = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_pred_scatter == 2],
                                                        sig_ref[self.df_1.signals_pred_scatter == 2],
                                                        size=size_1, pen='#00FF7F', symbol='t1', brush='#1E1E1E')
            # Scatter2 Short y_pred
            self.scatter_short_pred = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_pred_scatter == -1],
                                                         sig_ref[self.df_1.signals_pred_scatter == -1],
                                                         size=size_1, pen='#FF0000', symbol='t', brush='#8B0000')

        else:
            # Scatter1 Long y_true
            self.scatter_long_true = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_true_scatter == 1],
                                                        sig_ref[self.df_1.signals_true_scatter == 1],
                                                        size=size_1, pen='#00FF7F', symbol='t1', brush='#008B00')
            # Scatter1 Short y_true
            self.scatter_short_true = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_true_scatter == -1],
                                                         sig_ref[self.df_1.signals_true_scatter == -1],
                                                         size=size_1, pen='#FF0000', symbol='t', brush='#8B0000')
            # Scatter2 Long y_pred
            self.scatter_long_pred = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_pred_scatter == 1],
                                                        sig_ref[self.df_1.signals_pred_scatter == 1],
                                                        size=size_1, pen='#00FF7F', symbol='t1', brush='#008B00')
            # Scatter2 Short y_pred
            self.scatter_short_pred = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_pred_scatter == -1],
                                                         sig_ref[self.df_1.signals_pred_scatter == -1],
                                                         size=size_1, pen='#FF0000', symbol='t', brush='#8B0000')
            # Scatter1 Exit y_true Long
            self.scatter_exit_true_long = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_true_scatter == -2],
                                                             sig_ref[self.df_1.signals_true_scatter == -2],
                                                             size=size_1, pen='#FF0000', symbol='t', brush='#1E1E1E')
            # Scatter1 Exit y_true Short
            self.scatter_exit_true_short = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_true_scatter == 2],
                                                              sig_ref[self.df_1.signals_true_scatter == 2],
                                                              size=size_1, pen='#00FF7F', symbol='t1', brush='#1E1E1E')
            # Scatter1 Exit y_pred Long
            self.scatter_exit_pred_long = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_pred_scatter == -2],
                                                             sig_ref[self.df_1.signals_pred_scatter == -2],
                                                             size=size_1, pen='#FF0000', symbol='t', brush='#1E1E1E')
            # Scatter1 Exit y_pred Short
            self.scatter_exit_pred_short = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_pred_scatter == 2],
                                                              sig_ref[self.df_1.signals_pred_scatter == 2],
                                                              size=size_1, pen='#00FF7F', symbol='t1', brush='#1E1E1E')

        # Scatter exit-gain y_true
        self.scatter_exit_gain_true = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_true_scatter == 4],
                                                         sig_ref[self.df_1.signals_true_scatter == 4],
                                                         size=size_2, pen='#FFFF00', symbol='+', brush='#FFFF00')
        # Scatter exit-stop y_true
        self.scatter_exit_stop_true = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_true_scatter == -4],
                                                         sig_ref[self.df_1.signals_true_scatter == -4],
                                                         size=size_2, pen='#FF00FF', symbol='x', brush='#1E1E1E')

        # Scatter exit-gain y_pred
        self.scatter_exit_gain_pred = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_pred_scatter == 4],
                                                         sig_ref[self.df_1.signals_pred_scatter == 4],
                                                         size=size_2, pen='#FFFF00', symbol='+', brush='#FFFF00')
        # Scatter exit-stop y_pred
        self.scatter_exit_stop_pred = pg.ScatterPlotItem(self.df_1.index[self.df_1.signals_pred_scatter == -4],
                                                         sig_ref[self.df_1.signals_pred_scatter == -4],
                                                         size=size_2, pen='#FF00FF', symbol='x', brush='#1E1E1E')

    def show_risk_metrics(self, N, rf):

        # Sharpe Ratio
        mean = self.strategy_returns_pred.mean() * N - (rf / 100)
        sigma = self.strategy_returns_pred.std() * np.sqrt(N)
        self.sharpe_ratio = mean / sigma

        # Sortino Ratio
        mean = self.strategy_returns_pred.mean() * N - (rf / 100)
        std_neg = self.strategy_returns_pred[self.strategy_returns_pred < 0].std() * np.sqrt(N)
        self.sortino_ratio = mean / std_neg

        # Calmar Ratio
        mean = self.strategy_returns_pred.mean() * N
        self.calmar_ratio = mean / abs(self.drawdown[0].min())

        text = "SHARPE: {}     ".format(round(self.sharpe_ratio, 2)) + \
               "SORTINO: {}     ".format(round(self.sortino_ratio, 2)) + \
               "CALMAR: {} ".format(round(self.calmar_ratio, 2))

        self.risk_metrics_textitem.setText(text=text)
        self.risk_metrics_textitem.show()

    @staticmethod
    def apply_tax(positions, strategy_returns_log, maker_tax):

        for i in range(len(strategy_returns_log)):

            if i > 1:

                if positions[i - 2] == 1 and positions[i - 1] == -1:
                    strategy_returns_log[i] = strategy_returns_log[i] - ((2 * float(maker_tax)) / 100)

                elif positions[i - 2] == -1 and positions[i - 1] == 1:
                    strategy_returns_log[i] = strategy_returns_log[i] - ((2 * float(maker_tax)) / 100)

                elif positions[i - 2] == 0 and positions[i - 1] != 0:
                    strategy_returns_log[i] = strategy_returns_log[i] - (float(maker_tax) / 100)

                elif positions[i - 2] != 0 and positions[i - 1] == 0:
                    strategy_returns_log[i] = strategy_returns_log[i] - (float(maker_tax) / 100)

                elif np.isnan(positions[i - 2]) and positions[i - 1] != 0:
                    strategy_returns_log[i] = strategy_returns_log[i] - (float(maker_tax) / 100)

        return strategy_returns_log

    @staticmethod
    def iter_df(df_1, pos_true, pos_pred, pct_rate, stop_rate, gain_rate, logic, amount):

        df_1.reset_index(drop=True, inplace=True)

        pos_var_1 = 0
        pos_var_2 = 0
        pos_var_3 = 0
        pos_var_4 = 0
        c_ref_true = 0
        c_ref_pred = 0
        df_1["positions_pred_ref"] = np.nan
        df_1["positions_true_ref"] = np.nan
        df_1['signals_true'] = np.nan
        df_1['signals_pred'] = np.nan
        df_1['signals_true_scatter'] = 0
        df_1['signals_pred_scatter'] = 0
        df_1['positions_pred'] = np.nan
        df_1['positions_true'] = np.nan
        df_1['amount_str'] = 0.0
        df_1.loc[0, 'amount_str'] = amount
        df_1['amount_hold'] = 0.0
        df_1.loc[0, 'amount_hold'] = amount

        if pct_rate is not None:

            pct_rate = pct_rate / 100

            if logic == "long":
                df_1.positions_true_ref = np.where(
                    df_1['true'] >= pct_rate, amount, np.where(df_1['true'] <= -pct_rate, 0.0, np.nan))
                df_1.positions_pred_ref = np.where(
                    df_1['pred'] >= pct_rate, amount, np.where(df_1['pred'] <= -pct_rate, 0.0, np.nan))
            elif logic == "short":
                df_1.positions_true_ref = np.where(
                    df_1['true'] >= pct_rate, 0.0, np.where(df_1['true'] <= -pct_rate, -amount, np.nan))
                df_1.positions_pred_ref = np.where(
                    df_1['pred'] >= pct_rate, 0.0, np.where(df_1['pred'] <= -pct_rate, -amount, np.nan))
            else:
                df_1.positions_true_ref = np.where(
                    df_1['true'] >= pct_rate, amount, np.where(df_1['true'] <= -pct_rate, -amount, np.nan))
                df_1.positions_pred_ref = np.where(
                    df_1['pred'] >= pct_rate, amount, np.where(df_1['pred'] <= -pct_rate, -amount, np.nan))

            df_1.positions_pred_ref.fillna(method='ffill', inplace=True)
            df_1.positions_pred_ref.fillna(0, inplace=True)
            df_1.positions_true_ref.fillna(method='ffill', inplace=True)
            df_1.positions_true_ref.fillna(0, inplace=True)

        else:
            df_1.positions_true_ref = pos_true
            df_1.positions_pred_ref = pos_pred

        # Signals / Signals_Size
        df_1["signals_size_pred"] = df_1.positions_pred_ref.diff()
        df_1.signals_size_pred.fillna(df_1.positions_pred_ref[0], inplace=True)
        df_1["signals_size_true"] = df_1.positions_true_ref.diff()
        df_1.signals_size_true.fillna(df_1.positions_true_ref[0], inplace=True)
        df_1["signals_pred"] = np.where(df_1.signals_size_pred > 0, 1, np.where(df_1.signals_size_pred < 0, -1, 0))
        df_1["signals_true"] = np.where(df_1.signals_size_true > 0, 1, np.where(df_1.signals_size_true < 0, -1, 0))

        # Positions
        df_1['positions_true'] = df_1.positions_true_ref / amount
        df_1['positions_pred'] = df_1.positions_pred_ref / amount

        for index in range(len(df_1)):

            if logic == "long":
                # True
                # Scatter Stop
                if df_1.positions_true[index] == 0 and pos_var_1 == 10:
                    df_1.signals_true_scatter.values[index] = 0
                    df_1.signals_true.values[index] = 0
                    pos_var_1 = 0
                # Scatter Long
                if df_1.positions_true[index] > 0 and df_1.signals_true[index] == 1:
                    pos_var_1 = 1
                    df_1.signals_true_scatter.values[index] = 1
                    c_ref_true = df_1.c.values[index]
                # Scatter Exit-Long
                elif df_1.positions_true[index] == 0 and df_1.signals_true[index] == -1:
                    pos_var_1 = 0
                    df_1.signals_true_scatter.values[index] = -2
                # Stop Loss/Gain Logic
                if pos_var_1 == 10:
                    df_1.positions_true.values[index] = 0

                # Pred
                # Scatter Stop
                if df_1.positions_pred[index] == 0 and pos_var_2 == 10:
                    df_1.signals_pred_scatter.values[index] = 0
                    df_1.signals_pred.values[index] = 0
                    pos_var_2 = 0
                # Scatter Long
                if df_1.positions_pred[index] > 0 and df_1.signals_pred[index] == 1:
                    pos_var_2 = 1
                    df_1.signals_pred_scatter.values[index] = 1
                    c_ref_pred = df_1.c.values[index]
                # Scatter Exit-Long
                elif df_1.positions_pred[index] == 0 and df_1.signals_pred[index] == -1:
                    pos_var_2 = 0
                    df_1.signals_pred_scatter.values[index] = -2
                # Stop Loss/Gain Logic
                if pos_var_2 == 10:
                    df_1.positions_pred.values[index] = 0

            if logic == "short":
                # True
                # Scatter Stop
                if df_1.positions_true[index] == 0 and pos_var_1 == -10:
                    df_1.signals_true_scatter.values[index] = 0
                    df_1.signals_true.values[index] = 0
                    pos_var_1 = 0
                # Scatter Short
                if df_1.positions_true[index] < 0 and df_1.signals_true[index] == -1:
                    pos_var_1 = -1
                    df_1.signals_true_scatter.values[index] = -1
                    c_ref_true = df_1.c.values[index]
                # Scatter Exit-Short
                elif df_1.positions_true[index] == 0 and df_1.signals_true[index] == 1:
                    pos_var_1 = 0
                    df_1.signals_true_scatter.values[index] = 2
                # Stop Loss/Gain Logic
                if pos_var_1 == -10:
                    df_1.positions_true.values[index] = 0

                # Pred
                # Scatter Stop
                if df_1.positions_pred[index] == 0 and pos_var_2 == -10:
                    df_1.signals_pred_scatter.values[index] = 0
                    df_1.signals_pred.values[index] = 0
                    pos_var_2 = 0
                # Scatter Short
                if df_1.positions_pred[index] < 0 and df_1.signals_pred[index] == -1:
                    pos_var_2 = -1
                    df_1.signals_pred_scatter.values[index] = -1
                    c_ref_pred = df_1.c.values[index]
                # Scatter Exit-Short
                elif df_1.positions_pred[index] == 0 and df_1.signals_pred[index] == 1:
                    pos_var_2 = 0
                    df_1.signals_pred_scatter.values[index] = 2
                # Stop Loss/Gain Logic
                if pos_var_2 == -10:
                    df_1.positions_pred.values[index] = 0

            if logic == "long-short":

                # True
                # Scatter Long
                if df_1.positions_true[index] > 0 and df_1.signals_true[index] == 1:
                    pos_var_1 = 1
                    df_1.signals_true_scatter.values[index] = 1
                    c_ref_true = df_1.c.values[index]
                # Scatter Short
                elif df_1.positions_true[index] < 0 and df_1.signals_true[index] == -1:
                    pos_var_1 = -1
                    df_1.signals_true_scatter.values[index] = -1
                    c_ref_true = df_1.c.values[index]
                # Stop Loss/Gain Logic
                if pos_var_1 == -10 or pos_var_1 == 10:
                    df_1.positions_true.values[index] = 0

                # Pred
                # Scatter Long
                if df_1.positions_pred[index] > 0 and df_1.signals_pred[index] == 1:
                    pos_var_2 = 1
                    df_1.signals_pred_scatter.values[index] = 1
                    c_ref_pred = df_1.c.values[index]
                # Scatter Short
                elif df_1.positions_pred[index] < 0 and df_1.signals_pred[index] == -1:
                    pos_var_2 = -1
                    df_1.signals_pred_scatter.values[index] = -1
                    c_ref_pred = df_1.c.values[index]
                # Stop Loss/Gain Logic
                if pos_var_2 == -10 or pos_var_2 == 10:
                    df_1.positions_pred.values[index] = 0

            if logic == "long-short-exit":
                # True
                # Stop Loss/Gain Logic
                if pos_var_3 == 20 and df_1.signals_true.values[index] != 0 and df_1.positions_true[index] != 0:
                    pos_var_3 = 0
                    pos_var_1 = 0
                # Scatter Long
                if df_1.positions_true[index] == 1 and df_1.signals_true[index] == 1:
                    pos_var_1 = 1
                    df_1.signals_true_scatter.values[index] = 1
                    c_ref_true = df_1.c.values[index]
                # Scatter Short
                elif df_1.positions_true[index] == -1 and df_1.signals_true[index] == -1:
                    pos_var_1 = -1
                    df_1.signals_true_scatter.values[index] = -1
                    c_ref_true = df_1.c.values[index]
                # Scatter Exit-Long
                elif df_1.positions_true[index] == 0 and df_1.signals_true[index] == -1 and pos_var_1 == 1:
                    pos_var_1 = 0
                    df_1.signals_true_scatter.values[index] = -2
                # Scatter Exit-Short
                elif df_1.positions_true[index] == 0 and df_1.signals_true[index] == 1 and pos_var_1 == -1:
                    pos_var_1 = 0
                    df_1.signals_true_scatter.values[index] = 2
                # Scatter Stop
                if pos_var_1 == -10 or pos_var_1 == 10:
                    pos_var_3 = 20
                    df_1.positions_true.values[index] = 0
                    df_1.signals_true.values[index] = 0

                # Pred
                # Stop Loss/Gain Logic
                if pos_var_4 == 20 and df_1.signals_pred.values[index] != 0 and df_1.positions_pred[index] != 0:
                    pos_var_4 = 0
                    pos_var_2 = 0
                # Scatter Long
                if df_1.positions_pred[index] == 1 and df_1.signals_pred[index] == 1:
                    pos_var_2 = 1
                    df_1.signals_pred_scatter.values[index] = 1
                    c_ref_pred = df_1.c.values[index]
                # Scatter Short
                elif df_1.positions_pred[index] == -1 and df_1.signals_pred[index] == -1:
                    pos_var_2 = -1
                    df_1.signals_pred_scatter.values[index] = -1
                    c_ref_pred = df_1.c.values[index]
                # Scatter Exit-Long
                elif df_1.positions_pred[index] == 0 and df_1.signals_pred[index] == -1 and pos_var_2 == 1:
                    pos_var_2 = 0
                    df_1.signals_pred_scatter.values[index] = -2
                # Scatter Exit-Short
                elif df_1.positions_pred[index] == 0 and df_1.signals_pred[index] == 1 and pos_var_2 == -1:
                    pos_var_2 = 0
                    df_1.signals_pred_scatter.values[index] = 2
                # Scatter Stop
                if pos_var_2 == -10 or pos_var_2 == 10:
                    pos_var_4 = 20
                    df_1.positions_pred.values[index] = 0
                    df_1.signals_pred.values[index] = 0

            if stop_rate is not None:
                # Stop long true
                if pos_var_1 == 1 and df_1.c.values[index] < c_ref_true - ((stop_rate / 100) * c_ref_true):
                    df_1.signals_true_scatter.values[index] = -4
                    df_1.positions_true.values[index] = 0
                    c_ref_true = 0
                    pos_var_1 = 10

                # Stop short true
                if pos_var_1 == -1 and df_1.c.values[index] > c_ref_true + ((stop_rate / 100) * c_ref_true):
                    df_1.signals_true_scatter.values[index] = -4
                    df_1.positions_true.values[index] = 0
                    c_ref_true = 0
                    pos_var_1 = -10

                # Stop long pred
                if pos_var_2 == 1 and df_1.c.values[index] < c_ref_pred - ((stop_rate / 100) * c_ref_pred):
                    df_1.signals_pred_scatter.values[index] = -4
                    df_1.positions_pred.values[index] = 0
                    c_ref_pred = 0
                    pos_var_2 = 10

                # Stop short pred
                if pos_var_2 == -1 and df_1.c.values[index] > c_ref_pred + ((stop_rate / 100) * c_ref_pred):
                    df_1.signals_pred_scatter.values[index] = -4
                    df_1.positions_pred.values[index] = 0
                    c_ref_pred = 0
                    pos_var_2 = -10

            if gain_rate is not None:
                # Gain long true
                if pos_var_1 == 1 and df_1.c.values[index] > c_ref_true + ((gain_rate / 100) * c_ref_true):
                    df_1.signals_true_scatter.values[index] = 4
                    df_1.positions_true.values[index] = 0
                    c_ref_true = 0
                    pos_var_1 = 10

                # Gain short true
                if pos_var_1 == -1 and df_1.c.values[index] < c_ref_true - ((gain_rate / 100) * c_ref_true):
                    df_1.signals_true_scatter.values[index] = 4
                    df_1.positions_true.values[index] = 0
                    c_ref_true = 0
                    pos_var_1 = -10

                # Gain long pred
                if pos_var_2 == 1 and df_1.c.values[index] > c_ref_pred + ((gain_rate / 100) * c_ref_pred):
                    df_1.signals_pred_scatter.values[index] = 4
                    df_1.positions_pred.values[index] = 0
                    c_ref_pred = 0
                    pos_var_2 = 10

                # Gain short pred
                if pos_var_2 == -1 and df_1.c.values[index] < c_ref_pred - ((gain_rate / 100) * c_ref_pred):
                    df_1.signals_pred_scatter.values[index] = 4
                    df_1.positions_pred.values[index] = 0
                    c_ref_pred = 0
                    pos_var_2 = -10

        # Update Signals / Signals_Size
        df_1["signals_size_true"] = df_1.positions_true.diff() * amount
        df_1.signals_size_true.fillna(df_1.positions_true_ref[0], inplace=True)
        df_1["signals_size_pred"] = df_1.positions_pred.diff() * amount
        df_1.signals_size_pred.fillna(df_1.positions_pred_ref[0], inplace=True)
        df_1["signals_true"] = np.where(df_1.signals_size_true > 0, 1, np.where(df_1.signals_size_true < 0, -1, 0))
        df_1["signals_pred"] = np.where(df_1.signals_size_pred > 0, 1, np.where(df_1.signals_size_pred < 0, -1, 0))

        return df_1

    @staticmethod
    def drawdowns(pnl):
        s = pnl.values
        highwatermark = np.zeros(len(s))
        drawdown = np.zeros(len(s))
        drawdowndur = np.zeros(len(s))

        for t in range(1, len(s)):
            highwatermark[t] = max(highwatermark[t - 1], s[t])
            drawdown[t] = - (highwatermark[t] - s[t])
            drawdowndur[t] = (0 if drawdown[t] == 0 else drawdowndur[t - 1] + 1)

        return [drawdown, drawdowndur]
