jQuery(function(){
    var noteConfig, tagConfig;
    var notes, tags;
    //normal comments
    commentConfig = {
        docRoot  : jQuery(".body"),
        tag_list : "p",
        interfaceLabel: "<img src='image/icons/comment_add.png'/>",
        replyLabel: " <img src='image/icons/comments_add.png'/>",
        serverAddress : "http://demo.adfi.usq.edu.au/",
        pageUri : window.location.href
    }
    notes = anotarFactory(jQuery, commentConfig);
    //tags - not in standalone or Moodle plugin of Anotar
    tagConfig = {
           docRoot: "#object-tag-list",
           tagList: "p",
           pageUri: window.location.href,
           uriAttr: "rel",
           outputInChild: ".object-tags",
           annotationType: "tag",
           stylePrefix: "tags-",
           interfaceLabel: " <img src='images/icons/add.png'/>",
           formPrepend: true,
           interfaceVisible: true,
           serverAddress: "http://demo.adfi.usq.edu.au/",
           disableReply: true,
    }
    tag = anotarFactory(jQ, tagConfig);
});
