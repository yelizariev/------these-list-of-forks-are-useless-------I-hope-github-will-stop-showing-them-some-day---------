import sys
import os
import subprocess

import polib
from google.cloud import translate_v2 as translate
translate_client = translate.Client()


def translate_po(src_lang, dest_lang, folder):

    src_fname = os.path.join(folder, '%s.po' % src_lang)
    dest_fname = os.path.join(folder, '%s.po' % dest_lang)
    if not os.path.exists(src_fname):
        print ("Source file doesn't exist: %s" % src_fname)
        return

    if not os.path.exists(dest_fname):
        print ("Target file doesn't exist: %s" % dest_fname)
        subprocess.check_output(["cp %s" % os.path.join(folder, '*.pot'), dest_fname])

    src_po = polib.pofile(src_fname)
    dest_po = polib.pofile(dest_fname)

    for dest_entry in dest_po:
        if dest_entry.msgstr:
            # already translated
            continue
        src_entry = src_po.find(dest_entry.msgid)
        if not src_entry:
            print ("%s: source entry not found or empty: \n%s\n" % (src_fname, dest_entry.msgid))
            continue

        if src_entry.msgstr == src_entry.msgid:
            # Not for translattion.
            # Just copy original.
            # If we leave it empty, transifex will always offer to translate it, which is annoying
            dest_entry.msgstr = src_entry.msgid
            continue

        tr_text = translate_text(src_entry.msgstr, src_lang, dest_lang)
        dest_entry.msgstr = tr_text

    dest_po.save()


def translate_text(text, src, dest):
    result = translate_client.translate(text, source_language=src, target_language=dest)
    return result['translatedText']


if __name__ == '__main__':
    print (sys.argv)
    src_lang = sys.argv[1]
    dest_lang = sys.argv[2]
    folder = sys.argv[3]
    translate_po(src_lang, dest_lang, folder)
