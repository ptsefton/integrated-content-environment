#!/usr/bin/env python

import unittest, types
from unittest import TestCase, TextTestRunner, TestLoader, TestResult, defaultTestLoader as testLoader
from triplink import TripLink, Triple

from urlparse import urlsplit, parse_qs

from sys import path
path.append("../../../utils")
import xml_util

aNode1 = '<a href="http://ontologize.me/meta/?tl_p=http://purl.org/dc/terms/creator&amp;tl_o=http://trove.nla.gov.au/people/541658&amp;triplink=http://purl.org/triplink/v/0.1">ontologize</a>'
aNode1Href = 'http://ontologize.me/meta/?tl_p=http://purl.org/dc/terms/creator&amp;tl_o=http://trove.nla.gov.au/people/541658&amp;triplink=http://purl.org/triplink/v/0.1'

aNode2 = '<a href="http://ontologize.me/?tl_p=http://purl.org/dc/terms/subject&amp;triplink=http://purl.org/triplink/v/0.1&amp;tl_o=http://pir.georgetown.edu/cgi-bin/pro/entry_pro?id=PRO_000023043">katG</a>'
aNode2Href ='http://ontologize.me/?tl_p=http://purl.org/dc/terms/subject&amp;triplink=http://purl.org/triplink/v/0.1&amp;tl_o=http://pir.georgetown.edu/cgi-bin/pro/entry_pro?id=PRO_000023043'

aNode3 = '<a href="http://ontologize.me/?tl_p=http://xxxx.org/dc/terms/subject&amp;triplink=http://purl.org/triplink/v/0.1&amp;tl_o=http://pir.georgetown.edu/cgi-bin/pro/entry_pro?id=PRO_000023043">katG</a>'
aNode3Href ='http://ontologize.me/?tl_p=http://xxxx.org/dc/terms/subject&amp;triplink=http://purl.org/triplink/v/0.1&amp;tl_o=http://pir.georgetown.edu/cgi-bin/pro/entry_pro?id=PRO_000023043'

link1 = "http://ontologize.me/meta/?tl_p=http://purl.org/dc/terms/creator&tl_o=http://trove.nla.gov.au/people/541658&triplink=http://purl.org/triplink/v/0.1"
link2 = "http://dx.doi.org/10.1002/asi.4630270505?triplink=http://purl.org/triplink/v/0.1&tl_p=http://purl.org/spar/cito/cites"

link3 = "http://ontologize.me/?tl_p=http://purl.org/dc/terms/subject&triplink=http://purl.org/triplink/v/0.1&tl_o=http://pir.georgetown.edu/cgi-bin/pro/entry_pro?id=PRO_000023043"



aNode4 = '<a href="http://ontologize.me/?tl_p=http://www.xml-cml.org/convention/crystallographyExperiment&triplink=http://purl.org/triplink/v/0.1&tl_o=http://localhost:9997/portal/default/detail/6dc996c351d186e24f413279756c83db/">xxx</a>'
aNode4Href = "http://ontologize.me/?tl_p=http://www.xml-cml.org/convention/crystallographyExperiment&triplink=http://purl.org/triplink/v/0.1&tl_o=http://localhost:9997/portal/default/detail/6dc996c351d186e24f413279756c83db/"


class TripLinkTests(TestCase):
    def setUp(self):
        self.xml = xml_util.xml
        pass

    def tearDown(self):
        pass

    def testTriple1(self):
        urlParts = urlsplit(link1)
        query = urlParts.query
        params = parse_qs(query)
        
        triple = Triple (params, urlParts)
        self.assertEqual(triple.subject, ".")
        self.assertEqual(triple.predicate, "http://purl.org/dc/terms/creator")
        self.assertEqual(triple.object, "http://trove.nla.gov.au/people/541658")
        self.assertEqual(triple.isValid, True)

    def testTriple2(self):
        urlParts = urlsplit(link2)
        query = urlParts.query
        params = parse_qs(query)
        triple = Triple (params, urlParts)
        self.assertEqual(triple.subject, ".")
        self.assertEqual(triple.predicate, "http://purl.org/spar/cito/cites")
        self.assertEqual(triple.object, "http://dx.doi.org/10.1002/asi.4630270505")
        self.assertEqual(triple.isValid, True)

   

    def testParsing1(self):
        tripLink = TripLink()
        data = tripLink.process(aNode1Href,aNode1)
        self.assertEqual(data.get("dc"), "<dc:creator xmlns:dc='http://purl.org/dc/elements/1.1/'>ontologize (http://trove.nla.gov.au/people/541658)<dc:creator>")
        self.assertEqual(data.get("urltitle"), "This person or agent is a creator of this resource: (http://trove.nla.gov.au/people/541658)")
        self.assertEqual(data.get("dc_metadata"), ['creator', 'ontologize (http://trove.nla.gov.au/people/541658)'])
        self.assertEqual(data.get("RDFaTemplate"), u"""<span rel='http://purl.org/dc/elements/1.1/dc:creator' resource='http://trove.nla.gov.au/people/541658'/><span property='http://xmlns.com/foaf/0.1/foaf:name' resource='http://trove.nla.gov.au/people/541658'><a href="http://ontologize.me/meta/?tl_p=http://purl.org/dc/terms/creator&amp;tl_o=http://trove.nla.gov.au/people/541658&amp;triplink=http://purl.org/triplink/v/0.1">ontologize</a></span></span>""")
        self.assertEqual(data.get("readableMetadata"), ['author', 'ontologize (http://trove.nla.gov.au/people/541658)'])


    def testParsing2(self):
        tripLink = TripLink()
        data = tripLink.process(aNode2Href,aNode2)
        self.assertEqual(data.get("RDFaTemplate"), u"<span rel='http://purl.org/dc/elements/1.1/subject'><a href=\"http://ontologize.me/?tl_p=http://purl.org/dc/terms/subject&amp;triplink=http://purl.org/triplink/v/0.1&amp;tl_o=http://pir.georgetown.edu/cgi-bin/pro/entry_pro?id=PRO_000023043\">katG</a></span>")

    def testParsing4(self):
        tripLink = TripLink()
        data = tripLink.process(aNode4Href,aNode4)
        self.assertEqual(data.get("RDFaTemplate"), u"<span rel='http://www.xml-cml.org/convention/crystallographyExperiment' resource='http://localhost:9997/portal/default/detail/6dc996c351d186e24f413279756c83db/'><a href='http://localhost:9997/portal/default/detail/6dc996c351d186e24f413279756c83db/'>xxx</a></span>")

    def testParsingJustLinks(self):
        tripLink = TripLink();
        self.assertEqual(tripLink.process(link3)['urltitle'], "This work is about http://pir.georgetown.edu/cgi-bin/pro/entry_pro?id=PRO_000023043")

    def testDefault(self):
        tripLink = TripLink();
        data = tripLink.process(aNode3Href,aNode3)
        self.assertEqual(data["urltitle"], "Predicate: http://xxxx.org/dc/terms/subject Object: http://pir.georgetown.edu/cgi-bin/pro/entry_pro?id=PRO_000023043)")
        self.assertEqual(data.get("RDFaTemplate"), u"<span rel='http://xxxx.org/dc/terms/subject' resource='http://pir.georgetown.edu/cgi-bin/pro/entry_pro?id=PRO_000023043'><a href=\"http://ontologize.me/?tl_p=http://xxxx.org/dc/terms/subject&amp;triplink=http://purl.org/triplink/v/0.1&amp;tl_o=http://pir.georgetown.edu/cgi-bin/pro/entry_pro?id=PRO_000023043\">katG</a></span>")



if __name__ == "__main__":
    import sys
    print
    print
    print "---- Testing ----"
    print

    # Run only the selected tests
    #  Test Attribute testXxxx.slowTest = True
    #  fastOnly (do not run any slow tests)
    args = list(sys.argv)
    sys.argv = sys.argv[:1]
    args.pop(0)
    runTests = ["Add", "testAddGetRemoveImage"]
    runTests = args
    runTests = [ i.lower().strip(", ") for i in runTests]
    runTests = ["test"+i for i in runTests if not i.startswith("test")] + \
                [i for i in runTests if i.startswith("test")]
    if runTests!=[]:
        testClasses = [i for i in locals().values() \
                        if hasattr(i, "__bases__") and TestCase in i.__bases__]
        for x in testClasses:
            l = dir(x)
            l = [ i for i in l if i.startswith("test") and callable(getattr(x, i))]
            testing = []
            for i in l:
                if i.lower() not in runTests:
                    #print "Removing '%s'" % i
                    delattr(x, i)
                else:
                    #print "Testing '%s'" % i
                    testing.append(i)
        x = None
        print "Running %s selected tests - %s" % (len(testing), str(testing)[1:-1])

    unittest.main()



