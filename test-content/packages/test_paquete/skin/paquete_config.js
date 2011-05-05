 $(function(){        
     var paquete;
     paquete = paqueteFactory($);
     paquete.contentSelector = "div.body";
     paquete.titleSelector = "div.title"; 
     paquete.tocSelector = "div.paquete-toc";
     paquete.contentBaseUrl = "./";
     paquete.useNavigation = true; 
     paquete.navFormSettings = {
            prevLabel:"<img src='skin/paquete/images/previous.gif' title='Previous' />",
            nextLabel : "<img src='skin/paquete/images/next.gif' title='Next'/>",
            topLabel : " <img src='skin/paquete/images/top.gif' title='Top'/> ",
            inactivePrevLabel:"<img src='skin/paquete/images/inactive_previous.gif' title='Previous' />",
            inactiveNextLabel:"<img src='skin/paquete/images/inactive_next.gif' title='Next' />",
            inactiveTopLabel:"<img src='skin/paquete/images/inactive_up.gif' title='Top' />"
        }
     paquete.getManifestJson("manifest.json");
}); 