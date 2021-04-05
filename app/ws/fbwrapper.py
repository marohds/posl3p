# This Python file uses the following encoding: utf-8
import os
from sqlite3 import OperationalError
from websocket import create_connection
import websocket
import json
import unidecode
import logging
from pprint import pprint

class FBWrapper():

    @staticmethod
    def send(msg):
        ws = None
        try:
            ws = create_connection("ws://localhost:12000/ws")
            ws.send(msg)
            logging.info("Enviado '%s'" % msg)
            rta = ws.recv()
            logging.info("Recibido '%s'" % rta)
            ws.close()
            return True, None, rta
        except ConnectionRefusedError as e:
            if (not ws is None):
                 ws.close()
            logging.error(str(e))
            return False, "No se pudo conectar.<br />Por favor verifique el estado del programa de impresión", None
        except Exception as e:
            if (not ws is None):
                ws.close()
            logging.error(str(e))

    @staticmethod
    def validarRespuesta(rtadict):
        # {"rta": [{"action": "printTicket", "rta": null}]}
        pprint(rtadict)
        if (rtadict["rta"][0]["rta"] == None):
            return False, "No se pudo obtener una respuesta del la impresora.<br />Verifique el estado del programa de impresión"
        msg = None
        rtajson = json.loads(rtadict["rta"][0]["rta"])
        pprint(rtajson)
        # estado_impresora = (len(rtajson["Estado"]["Impresora"]) == 0)
        pprint(rtajson["Estado"])
        estado_impresora = (len(rtajson["Estado"].Impresora) == 0)
        pprint(estado_impresora)
        # estado_fiscal = (len(rtajson["Estado"]["Fiscal"]) == 0)
        estado_fiscal = (len(rtajson["Estado"].Fiscal) == 0)
        if (not estado_impresora):
            msg = str(rtajson["Estado"].Impresora[0])
        if (not estado_impresora):
            msg = str(rtajson["Estado"].Fiscal[0])
        result = (estado_impresora and estado_fiscal)
        return result,msg

    @staticmethod
    def cierreZ():
        cierreZJson = {"dailyClose":"Z","printerName":"IMPRESORA_FISCAL"}
        cierreZJson = json.dumps(cierreZJson)
        result,msg,rta = FBWrapper.send(cierreZJson)
        if (result):
            rta = json.loads(rta)
            result,msg = FBWrapper.validarRespuesta(rta)
        return result,msg,rta


    @staticmethod
    def imprimirTicket(venta):
        items = []
        for ventaItem in venta.items:
            item = {
                "alic_iva":str(ventaItem.product.iva),
                "importe":str(ventaItem.precio_venta),
                "ds":unidecode.unidecode(ventaItem.product.nombre),
                "qty":str(ventaItem.cantidad)
                }
            # Para descuento, hay que ver como recalcular iva.
            # discount=0, discountDescription=''
            items.append(item)

        printTicket = {
            "printTicket":{
                "encabezado":{"tipo_cbte":"T"},
                "items":items
                },
                "printerName":"IMPRESORA_FISCAL"}
        jsonTicket = json.dumps(printTicket)
        result,msg,rta = FBWrapper.send(jsonTicket)
        if (result):
            rta = json.loads(rta)
            result,msg = FBWrapper.validarRespuesta(rta)

        return result,msg,rta
        # {"printTicket":{"encabezado":{"tipo_cbte":"T"},"items":[{"alic_iva":21,"importe":0.01,"ds":"PEPSI","qty":1},{"alic_iva":21,"importe":0.12,"ds":"COCA","qty":2}]},"printerName":"IMPRESORA_FISCAL"}

    @staticmethod
    def listaImpresoras():
        result = FBWrapper.send('{"getAvaliablePrinters":""}')
        lista = json.loads(result)
        return lista["rta"]["rta"]


