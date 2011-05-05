 $(function(){        
     var paquete;
     paquete = paqueteFactory($);
     paquete.contentSelector = "div.body";
     paquete.titleSelector = "div.title"; 
     paquete.tocSelector = "div.paquete-toc";
     paquete.contentBaseUrl = "./";
     paquete.useNavigation = true; 
     paquete.navFormSettings = {
            prevLabel:"<img src='../images/previous.gif' title='Previous' />",
            nextLabel : "<img src='../images/next.gif' title='Next'/>",
            topLabel : " <img src='../images/top.gif' title='Top'/> ",
            inactivePrevLabel:"<img src='../images/inactive_previous.gif' title='Previous' />",
            inactiveNextLabel:"<img src='../images/inactive_next.gif' title='Next' />",
            inactiveTopLabel:"<img src='../images/inactive_up.gif' title='Top' />"
        }
     paquete.openLeafClass = "";
     paquete.closedLeafClass = "hide";
     paquete.getManifestJson("manifest.json");
}); 