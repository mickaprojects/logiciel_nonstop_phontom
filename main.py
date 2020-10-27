#!/usr/bin/env python
# -*- coding: cp1252 -*-

import psycopg2
import psycopg2.extras

from selenium.webdriver.common.keys import Keys
import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re, uuid
from selenium.webdriver.common.action_chains import ActionChains
from distutils.version import StrictVersion
from numbers import Number
from configparser import ConfigParser
import selenium.webdriver.support.ui as ui
from selenium.webdriver.support import expected_conditions as EC
from openpyxl.workbook import Workbook
import ast

from datetime import date
import time
import datetime
import sys
import os
import random
import glob
import re
import shutil
import traceback, wx
import fonctions

reload(sys)
sys.setdefaultencoding("cp1252")




class MainApp(wx.App):
    def OnInit(self):
        frame = menu()
        return True

class menu:
    def __init__(self,commande='',matricule=4546):
        if os.path.exists("main.lock")==False:
            try:
                lock=open("main.lock", "a")
                lock.close()
                k = 0

                #28 06 2018 python27
                trace = open("trace.txt", "w")
                trace.close()

                dbname="saisie"
                self.dbname = dbname

                it=fonctions.fonction()
                self.it=it

                self.it.createdb(self.dbname)

                try:
                    local      = psycopg2.connect("dbname="+self.dbname+" user=postgres password=123456  host= localhost") #prod
                    local.set_client_encoding('WIN1252')
                    local.set_isolation_level(0)
                    curlocal  = local.cursor(cursor_factory=psycopg2.extras.DictCursor);

                except :
                    dialogue       = wx.MessageDialog(None, 'Serveur local introuvable!', "Connexion!",wx.OK)
                    result         = dialogue.ShowModal()
                    return False

                sql="""
                        CREATE TABLE leboncoin
                        (
                          \"libelle\" character varying,
                          \"tel\" character varying(254),
                          \"flag\" character varying(254) DEFAULT 'n'::character varying,
                          idenr serial NOT NULL,
                          date_saisie date DEFAULT ('now'::text)::date,
                          CONSTRAINT pk_leboncoin PRIMARY KEY (idenr )
                        )
                        WITH (
                          OIDS=TRUE
                        );
                        ALTER TABLE leboncoin OWNER TO postgres;

                   """
                try:
                    curlocal.execute(sql)
                    local.commit()
                except:
                    pass

                date_jour1 = str(date.today())
                date_jour=self.date2fr(date_jour1,"/")
                # if(os.access(r"liste_tel.txt",os.F_OK)==False):
                #     trace = open("trace.txt", "a")
                #     trace.write("La liste du telephone est introuvable\n")
                #     trace.close()
                #     # print("La liste du telephone est introuvable")
                #     sys.exit(0)

                # if(os.access(r"liste_couleur.txt",os.F_OK)==False):
                #     trace = open("trace.txt", "a")
                #     trace.write("La liste du code couleur est introuvable\n")
                #     trace.close()
                #     # print("La liste du code couleur est introuvable")
                #     sys.exit(0)

                liste_couleur=[]
                liste_code=[]
                liste_code_couleur=[]
                # with open(r"liste_couleur.txt", "r") as f :
                #     fichier_entier = f.read()
                #     if fichier_entier!="":
                #         lignes = fichier_entier.split("\n")
                #         liste_code_couleur=lignes
                for c in liste_code_couleur:
                    s=c.split(":")
                    liste_code.append(s[0])
                    liste_couleur.append(s[1])

                nom_parametre = r"" + "parametres.ini"
                if (os.access(nom_parametre, os.F_OK) == False):
                    trace = open("trace.txt", "a")
                    trace.write("Le fichier parametres.ini est introuvable !\n")
                    trace.close()
                    # print("Le fichier parametres.ini est introuvable !")
                    sys.exit(0)

                config = ConfigParser()
                config.read(nom_parametre)

                temps_recherche = int(config.get('temps', 'temps_recherche'))
                temps_affichage_resultat = int(config.get('temps', 'temps_affichage_resultat'))
                temps_affichage_particulier = int(config.get('temps', 'temps_affichage_particulier'))
                temps_affichage_annonce = int(config.get('temps', 'temps_affichage_annonce'))
                temps_affichage_page = int(config.get('temps', 'temps_affichage_page'))
                temps_retour_accueil = int(config.get('temps', 'temps_retour_accueil'))
                toutes_categories = u""+str(config.get('parametre_moto', 'toutes_categories'))
                region = u"" + str(config.get('parametre_moto', 'region'))
                prix_min = u"" + str(config.get('parametre_moto', 'prix_min'))
                cylindree_min = u"" + str(config.get('parametre_moto', 'cylindree_min'))

                liste_tel=[]
                with open(r"liste_tel_debut_fin.txt", "r") as f :
                    fichier_entier = f.read()
                    if fichier_entier!="":
                        lignes = fichier_entier.split("\n")
                        liste_tel=lignes

                if len(liste_tel)==0:
                    trace = open("trace.txt", "a")
                    trace.write("La liste a rechercher est vide !"+"\n")
                    trace.close()
                    # print("La liste a rechercher est vide !")
                    sys.exit(0)

                debut=int(liste_tel[0].replace(" ","").strip())
                fin=int(liste_tel[1].replace(" ","").strip())
                # nom_fichier=datetime.datetime.today().strftime('%Y%m%d %H%M%S')+".txt"
                nom_fichier="resultats.txt"
                rep="resultats"
                sans_entete=False
                if os.path.exists(r""+"debut.txt")==True:
                    sans_entete=True
                    with open(r""+"debut.txt", "r") as f :
                        debut = int(f.read().replace(" ","").strip())

                if(os.access(rep,os.F_OK)==False):
                    os.makedirs(rep,777)

                chromeOptions = webdriver.ChromeOptions()
                chromeOptions.add_argument("--start-maximized")

                prefs = {"profile.default_content_settings.popups": 0,
                         "download.default_directory": "", # IMPORTANT - ENDING SLASH V IMPORTANT
                         "directory_upgrade": True, "extensions_to_open": "", "plugins.plugins_disabled": ["Chrome PDF Viewer"], "plugins.plugins_list": [{"enabled":False,"name":"Chrome PDF Viewer"}]}

                chromeOptions.add_experimental_option("prefs",prefs)
                chromeOptions.add_argument("--disable-print-preview")
                chromedriver = r"chromedriver.exe"
                driver = webdriver.Chrome(executable_path=chromedriver, chrome_options=chromeOptions)

                driver.implicitly_wait(temps_recherche)

                wait = ui.WebDriverWait(driver,temps_recherche)

                #Recuperation
                driver.get("https://www.leboncoin.fr/annonces/offres/rhone_alpes/")
                # driver.get("https://www.leboncoin.fr/recherche/?category=3&owner_type=private&price=1000-max&cubic_capacity=125-max&page=2")
                driver.maximize_window()

                #---categories----
                toutes_categories_ele=driver.find_element_by_xpath("//select[@data-qa-id='select-toggle_category']")
                select_cat = Select(toutes_categories_ele)
                select_cat.select_by_visible_text(toutes_categories)
                #---region----
                region_ele=driver.find_element_by_xpath("//select[@id='searcharea']")
                select_reg = Select(region_ele)
                select_reg.select_by_visible_text(region)
                #---prix_min----
                prix_min_ele=driver.find_element_by_xpath("//select[@data-qa-id='select-price_min']")
                select_prix_min = Select(prix_min_ele)
                select_prix_min.select_by_visible_text(prix_min)
                #---cylindree min----
                cylindree_min_ele=driver.find_element_by_xpath("//select[@data-qa-id='select-cubic_capacity_min']")
                select_cyl_min = Select(cylindree_min_ele)
                select_cyl_min.select_by_visible_text(cylindree_min)
                # --bouton recherche
                driver.find_element_by_xpath("//input[@data-qa-id='input-search_button']").click()
                time.sleep(temps_affichage_resultat)
                #---onglet particulier
                driver.find_element_by_xpath("//li[@id='react-tabs-2']").click()
                time.sleep(temps_affichage_particulier)
                # liste01=driver.find_elements_by_xpath("//div[@id='react-tabs-3']/div/ul/li")
                liste01=driver.find_elements_by_xpath("//div[@class='react-tabs__tab-panel react-tabs__tab-panel--selected']/div/ul/li")
                nombre_lignes=len(liste01)
                nombre_a_traiter=nombre_lignes-3
                # for x in range(nombre_lignes):
                # x=-1
                x=nombre_a_traiter
                current_url=driver.current_url
                page=1
                while True:
                    while True:
                        x=x+1
                        try:
                            # liste01=driver.find_elements_by_xpath("//div[@id='react-tabs-3']/div/ul/li")
                            liste01=driver.find_elements_by_xpath("//div[@class='react-tabs__tab-panel react-tabs__tab-panel--selected']/div/ul/li")
                            e1=liste01[x]
                            text01=e1.text
                            tab01=text01.split('\n')
                            libelle=""
                            if len(tab01)>=2:
                                libelle=tab01[1]
                            print(libelle)
                            trace = open("trace.txt", "a")
                            trace.write("***** "+libelle+"\n")
                            trace.close()

                            if libelle!="":
                                sql="select * from leboncoin where libelle='"+libelle.encode("cp1252").replace("'", "''")+"' and date_saisie='"+date_jour1+"'::date"
                                curlocal.execute(sql.encode("cp1252"))
                                t1=curlocal.fetchall()
                                if len(t1)==0:
                                    self.it.insertion("leboncoin",["libelle"], [libelle],local)
                                    trace = open("trace.txt", "a")
                                    trace.write("insertion"+"\n")
                                    trace.close()

                                    e1.click()
                                    trace = open("trace.txt", "a")
                                    trace.write("clic sur annonce"+"\n")
                                    trace.close()

                                    time.sleep(temps_affichage_annonce)
                                    driver.back()
                                    trace = open("trace.txt", "a")
                                    trace.write("retour page accueil"+"\n")
                                    trace.close()
                                    time.sleep(temps_retour_accueil)

                        except:
                            break
                    try:
                        page = page + 1
                        #print(current_url + "&page=" + str(page))
                        print("page {}".format(page))
                        li_s=driver.find_elements_by_xpath("//nav[@class='nMaRG']/div/ul/li")
                        li_s[page].click()
                        #driver.get(current_url + "&page=" + str(page))
                        trace = open("trace.txt", "a")
                        trace.write("passage page "+str(page)+"\n")
                        trace.close()

                        time.sleep(temps_affichage_page)
                    except Exception as inst:
                        break

                try:
                    driver.close()
                except:
                    pass

                trace = open("trace.txt", "a")
                trace.write("FIN Traitement recuperation donnees leboncoin !"+"\n")
                trace.close()

                #Suppression du fichier .lock
                if os.path.exists('main.lock')==True:
                    os.remove('main.lock')

                sys.exit(0)
                # print("FIN Traitement recuperation donnees !")

            except Exception as inst:
                log=open(date_jour.replace("/", "-")+".txt", "a")
                traceback.print_exc(file=log)
                log.close()
                try:
                    driver.close()
                except:
                    pass
                if os.path.exists('main.lock')==True:
                    os.remove('main.lock')

                sys.exit(0)


    def retour_valeur(self, tchamp, tvaleur, lib_champ):
        for l in range(len(lib_champ)):
            chp=lib_champ[l]
            for c in range(len(tchamp)):
                if tchamp[c].strip()==chp:
                    return u""+tvaleur[c].strip()
        return ""

    def libelle_couleur(self, liste_code, liste_couleur, code):
        for c in range(len(liste_code)):
            if liste_code[c]==code:
                return liste_couleur[c]
        return ""

    def nz(self, valeur_o,valeur_pardefaut=''):
        if valeur_o=='' or valeur_o==None or valeur_o=='None':
            return valeur_pardefaut
        else:
            return valeur_o

    def date2fr(self, sdateEn,sep="-"):
        a1=sdateEn[0:4]
        m1=sdateEn[5:7]
        d1=sdateEn[8:10]
        return d1+sep+m1+sep+a1

    def retour_lignes_fichier(self, sfichier):
        if os.path.exists(r""+sfichier)==False:
            return ""
        with open(r""+sfichier, "r") as f :
            fichier_entier = f.read()
            if fichier_entier!="":
                lignes = fichier_entier.split("\n")
                return lignes
            else:
                return ""

if __name__ == "__main__":
    app = MainApp()
    app.MainLoop()