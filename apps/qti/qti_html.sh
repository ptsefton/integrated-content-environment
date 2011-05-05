java -DproxySet=true -Dhttp.proxyHost=proxy.usq.edu.au -Dhttp.proxyPort=8000 org.apache.xalan.xslt.Process -XSL xsl/imsqti_to_xhtml.xsl -IN alpha.xml -OUT output/alpha.html ;
java -DproxySet=true -Dhttp.proxyHost=proxy.usq.edu.au -Dhttp.proxyPort=8000 org.apache.xalan.xslt.Process -XSL xsl/imsqti_to_xhtml.xsl -IN multipleselection.xml -OUT output/multipleselection.html ;
java -DproxySet=true -Dhttp.proxyHost=proxy.usq.edu.au -Dhttp.proxyPort=8000 org.apache.xalan.xslt.Process -XSL xsl/imsqti_to_xhtml.xsl -IN multiplechoice.xml -OUT output/multiplechoice.html ;

