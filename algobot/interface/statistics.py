import os
import re

from helpers import ROOT_DIR
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QDialog, QLabel, QTabWidget, QFormLayout

statisticsUi = os.path.join(ROOT_DIR, 'UI', 'statistics.ui')


class Statistics(QDialog):
    def __init__(self, parent=None):
        super(Statistics, self).__init__(parent)  # Initializing object
        uic.loadUi(statisticsUi, self)  # Loading the main UI
        self.tabs = {}

    @staticmethod
    def get_label_string(label: str) -> str:
        """
        Returns prettified string from a camel case formatted string.
        :param label: Potential string in camel case format.
        :return: Prettified string.
        """
        if not label[0].isupper():
            separated = re.sub('([A-Z][a-z]+)', r' \1', re.sub('([A-Z]+)', r' \1', label)).split()
            separated = list(map(lambda word: word.capitalize(), separated))
            label = ' '.join(separated)
        return label

    def remove_tab_if_needed(self, tabType):
        """
        Removes tab based on tabType provided (if it exists).
        :param tabType: Tab type to remove from list of statistics tabs.
        """
        if tabType in self.tabs:  # Delete previous tab if exists.
            tab = self.tabs[tabType]['tab']
            index = self.statisticsTabWidget.indexOf(tab)
            self.statisticsTabWidget.removeTab(index)

    def remove_old_tab(self, tabType):
        index = self.get_index_from_tab_type(tabType)
        self.statisticsTabWidget.removeTab(index)

    def initialize_tab(self, valueDictionary, tabType):
        """
        Initializes tab of tabType provided.
        :param valueDictionary: Dictionary with values to fill into the tab.
        :param tabType: Type of tab.
        """
        self.remove_old_tab(tabType)
        self.tabs[tabType] = {'tab': QTabWidget(), 'innerTabs': {}}  # Create new tab dictionary.

        tab = self.tabs[tabType]['tab']
        tab.setTabPosition(QTabWidget.West)

        index = self.get_index_from_tab_type(tabType)
        innerTabs = self.tabs[tabType]['innerTabs']

        for categoryKey in valueDictionary:
            self.add_category_and_children_keys(categoryKey, valueDictionary, innerTabs, tab)

        self.statisticsTabWidget.insertTab(index, tab, f"{tabType.capitalize()}")

    @staticmethod
    def get_index_from_tab_type(tabType):
        if 'sim' in tabType:
            return 1
        else:
            return 0

    def add_category_and_children_keys(self, categoryKey, valueDictionary, innerTabs, tab):
        """
        Modifies instance tabs variable with new values from valueDictionary.
        :param categoryKey: Category to modify.
        :param valueDictionary: Dictionary with values to put in.
        :param innerTabs: Inner tabs of tab to tbe modified. E.g. Simulation's inner tabs can be general, averages, etc.
        :param tab: Tab to be modified. For instance, this tab can be the simulation tab.
        """
        innerLayout = QFormLayout()
        innerTabs[categoryKey] = {'tab': QTabWidget()}

        for mainKey in valueDictionary[categoryKey]:
            label = QLabel(self.get_label_string(str(mainKey)))
            value = QLabel(str(valueDictionary[categoryKey][mainKey]))
            value.setAlignment(QtCore.Qt.AlignRight)

            innerLayout.addRow(label, value)
            innerTabs[categoryKey][mainKey] = {'label': label, 'value': value}

        innerTabs[categoryKey]['tab'].setLayout(innerLayout)
        tab.addTab(innerTabs[categoryKey]['tab'], self.get_label_string(categoryKey))

    @staticmethod
    def set_profit_or_loss_label(valueDictionary, innerTabs):
        if 'general' in valueDictionary and 'profit' in valueDictionary['general']:
            tab = innerTabs['general']
            if 'profit' in tab:
                if valueDictionary['general']['profit'][1] == '-':
                    label = 'Loss'
                    valueDictionary['general']['profit'] = "$" + valueDictionary['general']['profit'][2:]
                else:
                    label = 'Profit'
                tab['profit']['label'].setText(label)

    def modify_tab(self, valueDictionary, tabType):
        """
        Modifies tab.
        :param valueDictionary: Dictionary with values.
        :param tabType: Tab type to be modified.
        """
        innerTabs = self.tabs[tabType]['innerTabs']  # live/widgets
        self.set_profit_or_loss_label(valueDictionary=valueDictionary, innerTabs=innerTabs)

        for categoryKey in valueDictionary:
            if categoryKey not in innerTabs:
                tab = self.tabs[tabType]['tab']
                self.add_category_and_children_keys(categoryKey, valueDictionary, innerTabs, tab)
            else:
                innerWidgets = innerTabs[categoryKey]  # live/widgets/general
                for mainKey in valueDictionary[categoryKey]:
                    if mainKey in innerWidgets:
                        innerWidgets[mainKey]['value'].setText(str(valueDictionary[categoryKey][mainKey]))
                    else:
                        label = QLabel(self.get_label_string(str(mainKey)))
                        value = QLabel(str(valueDictionary[categoryKey][mainKey]))
                        value.setAlignment(QtCore.Qt.AlignRight)

                        layout = innerTabs[categoryKey]['tab'].layout()
                        layout.addRow(label, value)
                        innerWidgets[mainKey] = {'label': label, 'value': value}
