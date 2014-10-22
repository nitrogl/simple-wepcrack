pyuic4 interface/AboutBox.ui -o Ui_AboutBox.py
pyrcc4 res/AboutBox.qrc -o AboutBox_rc.py


# xgettext -L python SimpleWEPCracker.pyw
for i in it_IT
do
  cd "lang/$i/"
  msgfmt messages.po -o LC_MESSAGES/messages.mo
  cd ../../../
  echo "\"$i\" language compiled."
done