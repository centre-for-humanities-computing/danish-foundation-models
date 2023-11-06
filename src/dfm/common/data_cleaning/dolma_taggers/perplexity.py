"""
Perplexity taggers

This module contain taggers based on language models
"""
import hashlib
import logging
import os
import requests

import kenlm

from dolma.core.data_types import DocResult, Document, Span
from dolma.core.registry import TaggerRegistry
from dolma.core.taggers import BaseTagger
from dolma.core.utils import split_paragraphs

ccnet_sha256 = {
"af.arpa.bin":"7278e70cb22e29e94942b103c0ba49f406a9369c2949199fdf8d4bee4b0ce48e",
"ar.arpa.bin":"85739ba1e022a4abd9eb260e6c67e8a4e7646f0717e2800d8dde1ec039b7f5e2",
"az.arpa.bin":"247fd2355db94b4357d19c78c8ac38ce16299d1dac237745edeea8005d7771ba",
"be.arpa.bin":"b23a70aa0cec41555932e6b4aaa5a361c95d091fbd6d4c21e6a48c866b9cd1e8",
"bg.arpa.bin":"1edb68d25238d692cb9cc6b2e4f9fce0e99b49b421020c8e89d0781507dbcd38",
"bn.arpa.bin":"f21c8187eb77d2d7d17892b61dc3446dab79a61d3d0af4f0c90660f9df500cb2",
"ca.arpa.bin":"1e4e84639fd9a35cbfa47709ca2cd9eefc84dcee7ab7d91df11e5f89f88312d4",
"cs.arpa.bin":"4f89f980c12cae596b19fccd9aebea4be5be86c6f81a8b42fc975922ea656bb1",
"da.arpa.bin":"b7f754b56421944ada2c979d0b11e8eada8308e179cb60fbc1acc4318b03695b",
"de.arpa.bin":"a5bc18a9741dc57593d7cce469350d5d2db8ce1e87be6c2ec450850316e586ba",
"el.arpa.bin":"8a53a69835d0a8e88c720fc052180c54973d2b6ac3ed2ff83c666d432a0d3686",
"en.arpa.bin":"e90c9b25af01dcaa2667ed45d012d891269760fc6eccfe8dbbd161eb20e01d7d",
"es.arpa.bin":"00121ab8c31f275132fc67c292392a33ff81b8eae1015103e8a86f9df2e642d4",
"et.arpa.bin":"7c4b98dc3f7fff73611afdd0dc1379437cb0b3dd3addc0abadb65864cabb937f",
"fa.arpa.bin":"05d00d4fdb31e00295a63e4df4187954d43850a8bd7b61c717f809b19fc94cfe",
"fi.arpa.bin":"56aa4a6890c4152be3d594e7f7dc353e78881500803f36586c1c01d88f906618",
"fr.arpa.bin":"4a52387916be57551013df3f9052ee031c042445940a4d0e69b066597586c6aa",
"gu.arpa.bin":"4ad5be86ef47f3105eb9d7d178520a0cede5d02e4ca61a3aa2d32c8322ca5bd1",
"he.arpa.bin":"69d1ab538beb6c8aa646b7c611b701ad2d1a19dcce00d6690072fa9453ad2f00",
"hi.arpa.bin":"b7173df087ff5b24d759fdbf8d07d8e21a31c1b54c978c7c5c71f05b24e12f47",
"hr.arpa.bin":"3ba8caf473415c4d12be594c36892f1454a71a08441ad796bf105ebe4e957a8f",
"hu.arpa.bin":"ce82ceb8a1e808fc441d985c4249c08c67d527937d26e3e524404185803723cf",
"hy.arpa.bin":"3c5c3511a82538ab198536e54df4e770c40d78bf5929a7143ab42695641a0031",
"id.arpa.bin":"8e871368fb386180df09d1dfb45f0319dba7a1955b9d209e498c49d96d07b3dd",
"is.arpa.bin":"287f6f7bd8130d50df8966169427b236e9aa79ff2b4250c5bdfdc2c9a0c19f52",
"it.arpa.bin":"784efb647bd699041809d59dd309193f78a47ea347d13b0c93c3bd74f437a53b",
"ja.arpa.bin":"efa96d229e2a84be705f81bc4ea1c6da79505e5c7f001f92586e16481e5b586a",
"ka.arpa.bin":"07477bd9166bc2c748532f1c3af65aad42740231c0dc1f8a4410764e0d626199",
"kk.arpa.bin":"3cec2b6c9b3ae34919dd23ff59148e81b76593d7ec17feefcd5e2829cd1643c0",
"km.arpa.bin":"84a09db4e1e7a70e1cd7c347d9729339e3eaa993f42b4bba4ba91fe0a84ff763",
"kn.arpa.bin":"f1e0e469c8c78ac4e3b62d348e966e658cf7b8f683aafa4a2b4d55ca1e7d756c",
"ko.arpa.bin":"7e345046786a1ac6dbb0d3d0fdd65d2ff0e8a848395dbc84c6152acee1987f5f",
"lt.arpa.bin":"ecc1703e098477503035d980f6be841b5359f8f5f55cc4f78087232c7da15398",
"lv.arpa.bin":"5f6212551d5de115309674eed8ea595f1375973832917dd285942a0ef8d6c7e7",
"mk.arpa.bin":"0915b0c452f5bc6dd254c4145fd09f1252ea5e17f13f48991c72cb98fa2ed804",
"ml.arpa.bin":"3f0cfbf0bdc6935229d6903df8cb60b4ed2b9ed2cb9d4c253266b13bd3211297",
"mn.arpa.bin":"c8e57fcf604d178d45fbe3b1650c04e715c41cb8151bf8b115dc88c52ebfba56",
"mr.arpa.bin":"e00986484585cd67deba5902c7da78566452e3c40fc9aa285218152563d33303",
"my.arpa.bin":"ac3496e2981ea3ad85673ca52e04f5aa8e7be68d1d94c2e73ce26436864ae217",
"ne.arpa.bin":"7ef6c2d3e4e1858fb207e6c200e422833ccf072157a6a0148b408db3e760d22e",
"nl.arpa.bin":"aa017d97061e84f51d7f74b83a6a43aef246974fc9a502436043f6f0e9e12bbb",
"no.arpa.bin":"0ec663c264d6580beebe7e0e80a939dbe7082af55af3875f292ebd11ea5800de",
"pl.arpa.bin":"b97634bca2b28d95716b951ceadca3de4a170ff07639bcdc3c73fc0961362e98",
"pt.arpa.bin":"f5a10774d7b7125c6e887b62c56fea2d348adebc81ab1708d34f68de722090e0",
"ro.arpa.bin":"619b9a2d4d53bdb368bfdf2cc770e1e9549d52b22d1fd3afc0ee8a022543ed56",
"ru.arpa.bin":"588da7d3e160f61f7e821804bc4d518460687e1c4832c339bb3a28c03417ab53",
"uk.arpa.bin":"bfd09bdfe669a9fd5f8f8d9be519bdce3fb678214bc6afd5ccce499930b7d311",
"zh.arpa.bin":"f157d94cb2828bbb44b5dddf38e7eb7f62a47d317917646a73fe2af50a3dad68",
}

def _get_ccnet_pretrained_lm(lang: str):
    # Download pretrained model and save to the data folder
    url = f"http://dl.fbaipublicfiles.com/cc_net/lm/{lang}.arpa.bin"
    data_folder = "data_lm"

    if not os.path.exists(data_folder):
        os.makedirs(data_folder)

    filename = f"{lang}.arpa.bin"
    file_path = os.path.join(data_folder, filename)

    # Check if the file already exists
    if not os.path.exists(file_path):
        # If the file does not exist, download it
        logging.info(f"Downloading {lang} model...")
        response = requests.get(url)
        if response.status_code == requests.codes.ok:
            sha256 = hashlib.sha256(response.content).hexdigest()
            if sha256 != ccnet_sha256[filename]:
                raise RuntimeError(f"Checksum mismatch {sha256} != {ccnet_sha256[filename]}")
            with open(file_path, 'wb') as file:
                file.write(response.content)
            logging.info(f"{lang} model downloaded and saved at {file_path}")
        else:
            raise RuntimeError(f"Failed to download {lang} model. Status code: {response.status_code}")
    else:
        logging.info(f"{lang} model already exists at {file_path}")

    return file_path

def pp(log_score: float, length: float):
    """Convert total log-probability to perplexity"""
    return 10.0 ** (-log_score / length)

@TaggerRegistry.add("ccnet_paragraph_w_doc_da")
class CCNetDa(BaseTagger):
    def __init__(self):
        model_bin_path = _get_ccnet_pretrained_lm("da")
        self.model = kenlm.Model(model_bin_path)

    def predict(self, doc: Document) -> DocResult:
        paragraphs = split_paragraphs(doc.text)
        spans: list[Span] = []
        doc_log_prob: float = 0.0
        doc_length: float = 0.0
        for paragraph in paragraphs:
            log_prob = self.model.score(paragraph.text)
            length = len(paragraph.text.split()) + 1
            doc_log_prob += log_prob
            doc_length += length
            paragraph_span = Span(
                start=paragraph.start, end=paragraph.end, type="perplexity", score=pp(log_prob, length)
            )
            spans.append(paragraph_span)

        paragraph_span = Span(
            start=0, end=len(doc.text), type="doc_perplexity", score=pp(doc_log_prob, doc_length)
        )
        return DocResult(doc=doc, spans=spans)
