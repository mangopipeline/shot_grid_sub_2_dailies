'''
Created on Nov 30, 2021

@author: carlos.anguiano
'''
import os
from shot_grid_sub_2_dailies.sub2d_api import Sub2DAPI

from PySide2 import QtWidgets, QtUiTools, QtCore


class UiLoaderClass(object):
    def _add_my_ui_file(self, ui_file):
        # NOTE: let's make a basic layout
        self.mlayout = QtWidgets.QHBoxLayout(self)
        self.setLayout(self.mlayout)

        ui_file = QtCore.QFile(ui_file)
        ui_file.open(QtCore.QFile.ReadOnly)
        loader = QtUiTools.QUiLoader()

        mwidget = loader.load(ui_file, parent=self)
        self.mlayout.addWidget(mwidget)

        self.resize(mwidget.geometry().width(),
                    mwidget.geometry().height())

        self.setWindowTitle(mwidget.windowTitle())

        return mwidget


class CredDialog(QtWidgets.QDialog, UiLoaderClass):
    def __init__(self, api, parent=None):
        super(CredDialog, self).__init__(parent=parent)
        self.result = False
        self._api = api

        ui_file = os.path.join(os.path.dirname(
            __file__), 'views', 'creds.ui')

        self._mwidget = self._add_my_ui_file(ui_file)

        self._connect_signals()

    def _connect_signals(self):
        self._mwidget.pushButton.clicked.connect(self._register_creds)

    def _register_creds(self):
        try:
            self._api.set_cache_settings(self._mwidget.urlLineEdit.text(),
                                         self._mwidget.userLineEdit.text(),
                                         self._mwidget.passLineEdit.text(),
                                         is_user=self._mwidget.AuthTypeCheckBox.isChecked())
        except RuntimeError as msg:
            QtWidgets.QMessageBox.about(self,
                                        'Credential Error',
                                        str(msg))
            return
        # NOTE: if there is no error we bounce out let the tool do it's thing
        self.result = True
        self.close()


class MyApp(QtWidgets.QDialog, UiLoaderClass):
    def __init__(self, parent=None):
        super(MyApp, self).__init__(parent=parent)

        self.dont_open = False

        # NOTE let's make our main widget and add it to your app
        ui_file = os.path.join(os.path.dirname(
            __file__), 'views', 'mainWidget.ui')
        self._mwidget = self._add_my_ui_file(ui_file)

        self._api = Sub2DAPI()

        try:
            self._api.sg
        except RuntimeError:
            val = self._collect_creds()
            if not val:
                self.dont_open = True

        self._projects = []
        self._sequences = []
        self._shots = []
        self._tasks = []

        self._populate_projects()

        self._connect_signals()

    def _connect_signals(self):
        self._mwidget.PrjComboBox.currentIndexChanged.connect(lambda _: self._populate_sequences())
        self._mwidget.SeqComboBox.currentIndexChanged.connect(lambda _: self._popluate_shots())
        self._mwidget.shotComboBox.currentIndexChanged.connect(lambda _: self._populate_tasks())
        self._mwidget.LoadMediaBtn.clicked.connect(self._load_media)
        self._mwidget.SubmitButton.clicked.connect(self._submit_media)

    def _collect_creds(self):
        collect_creds = CredDialog(self._api, parent=self)
        collect_creds.exec_()
        return collect_creds.result

    def _populate_projects(self):
        self._projects = self._api.get_projects()
        self._mwidget.PrjComboBox.addItems([prj['name'] for prj in self._projects])

        self.blockSignals(True)
        self._populate_sequences()
        self.blockSignals(False)

    def _populate_sequences(self):
        self._sequences = []
        self._mwidget.SeqComboBox.clear()

        if not self._projects:
            self._popluate_shots()
            return

        prj = self._projects[self._mwidget.PrjComboBox.currentIndex()]
        self._sequences = self._api.get_sequences(prj)

        self._mwidget.SeqComboBox.addItems([seq['code'] for seq in self._sequences])

        self.blockSignals(True)
        self._popluate_shots()
        self.blockSignals(False)

    def _popluate_shots(self):
        self._shots = []
        self._mwidget.shotComboBox.clear()

        if not self._sequences:
            self._populate_tasks()
            return

        seq = self._sequences[self._mwidget.SeqComboBox.currentIndex()]
        self._shots = self._api.get_shots(seq)
        self._mwidget.shotComboBox.addItems([shot['code'] for shot in self._shots])

        self.blockSignals(True)
        self._populate_tasks()
        self.blockSignals(False)

    def _populate_tasks(self):
        self._tasks = []
        self._mwidget.TaskComboBox.clear()

        if not self._shots:
            return

        shot = self._shots[self._mwidget.shotComboBox.currentIndex()]
        self._tasks = self._api.get_tasks(shot)
        self._mwidget.TaskComboBox.addItems([task['cached_display_name'] for task in self._tasks])

    def _load_media(self):
        media_types = ['*%s' % key for key in Sub2DAPI.media_formats.keys()]
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self,
                                                             "Open Media",
                                                             "/home/jana",
                                                             "Image Files (%s)" % ' '.join(media_types))
        if not file_name:
            return

        self._mwidget.MediaPathLineEdit.setText(file_name)

    def _submit_media(self):
        task = None

        if self._tasks:
            task = self._tasks[self._mwidget.TaskComboBox.currentIndex()]

        if not task:
            QtWidgets.QMessageBox.about(self, 'Sub2Dailies', 'Please Select A Valid Task For Your Media')
            return

        media_path = self._mwidget.MediaPathLineEdit.text()
        if not os.path.isfile(media_path):
            QtWidgets.QMessageBox.about(self, 'Sub2Dailies', 'Please select media for upload')
            return

        comment = self._mwidget.MediaCommentPlainTextEdit.toPlainText()
        if not comment:
            QtWidgets.QMessageBox.about(self, 'Sub2Dailies', 'Please add a comment to your media')
            return

        self._api.upload_review_media(task,
                                      media_path,
                                      comment,
                                      qt_pg=self._mwidget.progressBar)
        QtWidgets.QMessageBox.about(self,
                                    'Sub2D',
                                    'Your media has been successfully submitted for review!')
        self.close()


if __name__ == '__main__':
    _APP = QtWidgets.QApplication([])
    _APP.setStyle('fusiion')
    _UI = MyApp()
    _UI.show()
    if _UI.dont_open:
        _UI.close()
    _APP.exec_()
