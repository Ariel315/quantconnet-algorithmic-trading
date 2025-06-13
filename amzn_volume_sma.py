# -*- coding: utf-8 -*-
"""amzn_volume_sma.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1AcfYdsrvvUkusszEsQWZBOT0sWlRbFgM
"""

from AlgorithmImports import *

class SleepyYellowGreenFlamingo(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(1997, 1, 1)
        self.SetCash(10000)

        self.symbol = self.AddEquity("AMZN", Resolution.DAILY, data_normalization_mode=DataNormalizationMode.Raw).Symbol
        self.Securities[self.symbol].SetFeeModel(ConstantFeeModel(0))

        self.SetWarmUp(timedelta(days=200))

        # Variables de control
        self.trade = False
        self.entry_time = None  # Marca de tiempo de entrada
        self.total_days_invested = 0  # Acumulador de días invertidos

        # Indicador de volumen
        self.volume_sma = self.SMA(self.symbol, 200, Resolution.DAILY, Field.Volume)

    def OnData(self, data: Slice):
        if self.IsWarmingUp:
            return

        trade_bar = data.Bars.get(self.symbol)
        if trade_bar is None or not self.volume_sma.IsReady:
            return

        current_volume = trade_bar.Volume
        average_volume = self.volume_sma.Current.Value

        # Regla de entrada: comprar si el volumen actual es 10 veces mayor que la media de los últimos 2000 volúmenes
        if not self.trade and current_volume >= 3 * average_volume:
            self.SetHoldings(self.symbol, 1)
            self.trade = True
            self.entry_time = self.Time
            self.Debug(f"Compra realizada. Volumen actual: {current_volume}, Media de volumen: {average_volume}")

        # Regla de salida: cerrar todas las operaciones si el volumen actual es menos de 5 veces mayor que la media
        if self.trade and current_volume < 2 * average_volume:
            self.Liquidate(self.symbol)
            self.trade = False

            # Calcular días invertidos
            days_invested = (self.Time - self.entry_time).days
            self.total_days_invested += days_invested
            self.entry_time = None
            self.Debug(f"Venta realizada. Volumen actual: {current_volume}, Días invertidos: {days_invested}")

    def OnEndOfAlgorithm(self):
        self.Debug(f"Tiempo total invertido en días: {self.total_days_invested:.2f}")