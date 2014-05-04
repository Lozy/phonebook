#!/usr/bin/env python
# -*- coding: utf-8 -*-

from xml.dom import minidom
from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
import base64
import copy
import os
from Crypto.Cipher import AES
from Crypto import Random

class Encryption():
    def __init__(self,key):
        self.bs = 32
        self.key = key

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))
    
    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

class xml_file:
    def __init__(self,filename):
        self.filename = filename
        self.xml_tostring = ET.tostring
        self.dataEncry = Encryption("FhpNdtHAJQb+Lan+gx4hOQ7x9IAQzRmh")
        
    def read(self):
        if os.path.isfile(self.filename) == False:
            result = {'contact':{}}
            self.write(result)
        else:
            f = open(self.filename,'r')
            fData = f.read()
            if fData == '':
                result = {'contact':{}}
            else:
                try:
                    result = self.xml2dict(fData)
                    if type(result['contact']) == list:
                        for item in result['contact']:
                            for key in item.keys():
                                item[key] = self.dataEncry.decrypt(item[key])
                    else:
                        for key in result['contact'].keys():
                                result['contact'][key] = self.dataEncry.decrypt(result['contact'][key])
                except:
                    result = {'contact':{}}
            f.close()
        return result

    def write(self,contact_dict):
        for item in contact_dict['contact']:
            for key in item.keys():
                item[key] = self.dataEncry.encrypt(item[key])
        tree_str = self.xml_tostring(self.dict2xml('contacts',contact_dict ))
        tree = minidom.parseString(tree_str)
        xml_string = tree.toprettyxml()
        try:
            f = open(self.filename,'w+')
            f.write(xml_string)
            f.close()
            return True
        except:
            return False
    
    def xml2dict(self,element):
        if type(element) in [str, unicode]:
            element = ET.fromstring(element)
        assert isinstance(element, Element)
        ret = {}
        for child in list(element):
            if len(child) != 0:
                value = self.xml2dict(child)
            else:
                value = child.text
            if child.tag in ret:
                if type(ret[child.tag]) != list:
                    ret[child.tag] = [ret[child.tag]]
                ret[child.tag].append(value)
            else:
                ret[child.tag] = value
        return ret

    def dict2xml(self,root, content):
        e = Element(root)
        if type(content) in [str, unicode, int, long, float]:
            e.text = content
            return e
    
        for key in content:
            if type(content[key]) == list:
                for one in content[key]:
                    e.append(self.dict2xml(key, one))
            else:
                e.append(self.dict2xml(key, content[key]))
        return e
    
class phone_DB:
    def __init__(self,xmlFile):
        self.dataHandle = xmlFile
        self.refresh()
        
    def refresh(self):
        self.data = self.dataHandle.read()
        if self.data == {}:
            self.data['contact'] = []
        elif type(self.data['contact']) == dict :
            if not self.data['contact']  == {}:
                temp = self.data['contact']
                self.data['contact']=[temp,]
            else:
                self.data['contact']=[]
        
    def sort(self,keyword):
        #import operator
        #sorted_contact = sorted(self.data['contact'], key=operator.itemgetter('id'))
        sorted_contact = sorted(self.data['contact'], key=lambda data: data[keyword])
        return sorted_contact
    
    def group(self):
        result={}
        for items in self.data['contact']:
            key = str( "%s" % items['group'] )
            if not result.has_key(key):
                result[key]=[items,]
            else:
                result[key].append(items)    
        return result
    
    def delete(self,contact_id):
        if filter(lambda x:x['id'] == str(contact_id),self.data['contact']) == []:
            print "Delete failed. person contact doesn't exist" 
            return False
        else:
            self.data['contact'] = filter(lambda x:x['id'] != str(contact_id),self.data['contact'])
            self.dataHandle.write(copy.deepcopy(self.data))
            return True
    
    def add(self,newContact):
        if not self.data['contact'] == []:
            newContact['id'] = str ( int ( self.data['contact'][-1]['id']) + 1  )
        else:
            newContact['id'] = '0'
        self.data['contact'].append(newContact)
        if self.dataHandle.write(copy.deepcopy( self.data )):
            return True
        else:
            return False
    
    def modify(self,contactData):
        if filter(lambda x:x['id'] == str(contactData['id']),self.data['contact']) == []:
            print "Modify failed. person contact doesn't exist!"
            return False
        else:
            for contact in self.data['contact']:
                if contact['id'] == contactData['id']:
                    cid = self.data['contact'].index(contact)
                    self.data['contact'][cid] = contactData
            self.dataHandle.write(copy.deepcopy( self.data ))
            return True
