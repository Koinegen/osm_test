import logging
import geocoder
import os.path
import argparse
import json
from difflib import SequenceMatcher
import re

class result():
	def __init__(self):
		self.good=0
		self.bad=0
		self.All=0
		self.soBad=0
		self.listOfBad=[]
		self.notWorking=[]
		
def checkForward(data,result):
	a=[]
	g=geocoder.osm(data.get("name"))
	a.append(g.osm.get('y'))
	a.append(g.osm.get('x'))
	if (len(data.get("name"))<20):
		logging.warning("Данных для проверки слишком мало")
		result.soBad+=1
		result.notWorking.append(data)
	elif (abs(a[0]-float(data.get('y')))<0.002 and abs(a[1]-float(data.get('x')))<0.002):
		logging.warning("Для\""+data.get("name")+"\" и y="+str(a[0])+" x="+str(a[1])+" координаты: " + str(data.get('y'))+" " + str(data.get('x'))+" верны.")
		logging.warning("\tТест пройден")
		result.good+=1
		result.All+=1
	else:
		logging.warning("Для \""+data.get("name")+"\" и y="+str(a[0])+" x="+str(a[1])+" координаты: "+str(data.get('y'))+" "+str(data.get('x'))+" не верны.")
		logging.warning("\tТест не пройден")
		result.bad+=1
		result.All+=1
		result.listOfBad.append(data)
		

def checkReverse(data,result):
	a=[]
	a.append(data.get('y'))
	a.append(data.get('x'))
	g=geocoder.osm(a,method='reverse')
	keys=g.osm.keys()
	testAddr=g.json.get('address')
	mainAddr=data.get('name')
	s = SequenceMatcher(lambda x: x==" ",testAddr,mainAddr)
	if (len(data.get("name"))<20):
		logging.warning("Данных для проверки слишком мало")
		result.soBad+=1
		result.notWorking.append(data)
	elif (float(s.ratio())>0.7):
		if ('addr:city' in keys and 'addr:street' in keys and 'addr:housenumber' in keys):
			readdr=g.osm.get('addr:housenumber')
			mainAdr=data.get('name')
			b=re.search(str(readdr),str(mainAdr),re.X|re.I)
			if (b != None):
				logging.warning("Для\"y="+str(a[0])+" x="+str(a[1])+" Адрес:"+mainAddr)
				logging.warning("Процент совпадения адреса: "+str(s.ratio()))
				logging.warning("\tТест пройден")
				result.good+=1
				result.All+=1
			else:
				logging.warning("Для\"y="+str(a[0])+" x="+str(a[1])+" Адрес:"+mainAddr+" и "+testAddr)
				logging.warning("Процент совпадения адреса: "+str(s.ratio())+", однако номера домов не совпали.")
				logging.warning("\tТест не пройден")
				result.bad+=1
				result.All+=1
				result.listOfBad.append(data)
				
		else:	
			logging.warning("Для\"y="+str(a[0])+" x="+str(a[1])+" Адрес:"+mainAddr)
			logging.warning("Процент совпадения адреса: "+str(s.ratio()))
			logging.warning("\tТест пройден")
			result.good+=1
			result.All+=1
	else:
		logging.warning("Для\"y="+str(a[0])+" x="+str(a[1])+" Адрес:"+mainAddr+" и "+testAddr)
		logging.warning("Процент совпадения адреса: "+str(s.ratio()))
		logging.warning("\tТест не пройден")
		result.bad+=1
		result.All+=1
		result.listOfBad.append(data)

def openFile(check,filepath):
	try:
		summary=result()
		f=open(filepath,'r')
		data = json.load(f)
		for i in data:
			try:
				check(i,summary)
			except:
				logging.warning("!!!Не обработанные данные!!!")
				summary.soBad+=1
				summary.notWorking.append(i)
		f.close()
		logging.warning("-------------------------------------------------------\nВсего обработано данных:"+str(summary.All)+"\nПрошли проверку:"+str(summary.good)+"\nНе прошли проверку:"+str(summary.bad)+"\nНе обработанные данные:"+str(summary.soBad)+"\n-------------------------------------------------------")
		logging.warning("Не обработанные данные:"+str(summary.notWorking)+"\n-------------------------------------------------------")
	except:
		logging.warning("Не верный формат данных или файл испорчен")
		print("Не верный формат файла или файл испорчен")
	try:
		f=open("bad_data.json","w")
		json.dump(summary.listOfBad,f,ensure_ascii=False)
		f.close()
		logging.warning("Входные данные не прошедшие проверку записаны в файл: bad_data.json")
		logging.warning("\tКонец лога")
	except:
		print("Файл с данными, не прошедшими проверку не записан!")
parser=argparse.ArgumentParser("give file for forward or reverse codings")
parser.add_argument('-f',type=str,help='-forward coding')
parser.add_argument('-r',type=str,help='-reverse coding')
parser.add_argument('-l','--log', type=str,help='-output file, default: results.log')
args=parser.parse_args()
if (args.log!=None):
	try:
		logging.basicConfig(filename=args.log,format='%(message)s',filemode='w',level=logging.WARNING)
		logging.warning("\n\tНачало лога!")
	except Exception as error:
		print(error)
		quit()
else:
	logging.basicConfig(filename="results.log",format='%(message)s',filemode='w',level=logging.WARNING)
	logging.warning("\n\tНачало лога!")
	
if (args.f!=None):
	fpath=args.f
	if (os.path.exists(fpath)):
		logging.warning("\tПрямое кодирование.")
		openFile(checkForward,fpath)
	else:
		print(fpath+" File not exists")
		quit()
elif (args.r!=None):
	fpath=args.r
	if (os.path.exists(fpath)):
		logging.warning("\tОбратное кодирование.")
		openFile(checkReverse,fpath)
	else:
		print(fpath+" File not exists")
		quit()
else:
	parser.print_help()