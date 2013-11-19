# -*- coding: utf-8 -*
import sqlite3
import time
import os
import uuid

class PyHarir(object):
    def __init__(self,dbpath):
        initScripts = [] if os.path.exists(dbpath) else ["""
CREATE TABLE "Classes"(
  "name" TEXT PRIMARY KEY NOT NULL,
  "version" INTEGER
);""","""
CREATE TABLE "Attributes"(
  "guid" TEXT PRIMARY KEY NOT NULL,
  "name" TEXT NOT NULL,
  "class" TEXT NOT NULL,
  "flags" INTEGER NOT NULL,
  "value" TEXT,
  "price" INTEGER NOT NULL,
  "type" INTEGER NOT NULL,
  "ftsMethod" TEXT,
  CONSTRAINT "name_UNIQUE"
    UNIQUE("name","class"),
  CONSTRAINT "fk_Attributes_Classes"
    FOREIGN KEY("class")
    REFERENCES "Classes"("name")
);""","""
CREATE TABLE "Nodes"(
  "id" TEXT PRIMARY KEY NOT NULL,
  "link" TEXT,
  "price" INTEGER NOT NULL
);""","""
CREATE TABLE "NodeValues"(
  "node" TEXT NOT NULL,
  "attr" TEXT NOT NULL,
  "value" TEXT COLLATE NOCASE,
  "bindNode" TEXT,
  "bindAttr" TEXT,
  "indexed" TEXT,
  PRIMARY KEY("node","attr"),
  CONSTRAINT "fk_Values_Attributes1"
    FOREIGN KEY("attr")
    REFERENCES "Attributes"("guid"),
  CONSTRAINT "fk_Values_Nodes1"
    FOREIGN KEY("node")
    REFERENCES "Nodes"("id"),
  CONSTRAINT "fk_NodeValues_NodeValues1"
    FOREIGN KEY("bindNode")
    REFERENCES "NodeValues"("node"),
  CONSTRAINT "fk_NodeValues_NodeValues2"
    FOREIGN KEY("bindAttr")
    REFERENCES "NodeValues"("attr")
);""","""
CREATE TABLE "Links"(
  "class" TEXT NOT NULL,
  "link" TEXT NOT NULL,
  PRIMARY KEY("class","link"),
  CONSTRAINT "fk_Links_Classes1"
    FOREIGN KEY("class")
    REFERENCES "Classes"("name"),
  CONSTRAINT "fk_Links_Classes2"
    FOREIGN KEY("link")
    REFERENCES "Classes"("name")
);""","""
CREATE TABLE "FullText"(
  "node" TEXT NOT NULL,
  "attr" TEXT NOT NULL,
  "value" TEXT NOT NULL COLLATE NOCASE,
  "pos" INTEGER NOT NULL,
  PRIMARY KEY("node","attr","value","pos"),
  CONSTRAINT "fk_FullText_NodeValues1"
    FOREIGN KEY("node")
    REFERENCES "NodeValues"("node"),
  CONSTRAINT "fk_FullText_NodeValues2"
    FOREIGN KEY("attr")
    REFERENCES "NodeValues"("node")
);""","""
CREATE TABLE "NodeVersions"(
  "node" TEXT NOT NULL,
  "class" TEXT NOT NULL,
  "version" TEXT,
  PRIMARY KEY("node","class"),
  CONSTRAINT "fk_NodeVersions_Nodes1"
    FOREIGN KEY("node")
    REFERENCES "Nodes"("id"),
  CONSTRAINT "fk_NodeVersions_Classes1"
    FOREIGN KEY("class")
    REFERENCES "Classes"("name")
);""","""
CREATE TABLE "Details"(
  "guid" TEXT PRIMARY KEY NOT NULL,
  "version" INTEGER NOT NULL,
  "writeAccess" BOOLEAN NOT NULL
);""","""
CREATE TABLE "Value3D"(
  "node" TEXT NOT NULL,
  "attr" TEXT NOT NULL,
  "id" TEXT NULL,
  "x0" DOUBLE NOT NULL DEFAULT 0,
  "x1" DOUBLE NOT NULL DEFAULT 0,
  "y0" DOUBLE NOT NULL DEFAULT 0,
  "y1" DOUBLE NOT NULL DEFAULT 0,
  "z0" DOUBLE NOT NULL DEFAULT 0,
  "z1" DOUBLE NOT NULL DEFAULT 0,
  PRIMARY KEY ("node", "attr"),
  CONSTRAINT "fk_Value3D_Nodes1"
    FOREIGN KEY ("node")
    REFERENCES "Nodes"("id"),
  CONSTRAINT "fk_Value3D_Attributes1"
    FOREIGN KEY ("attr")
    REFERENCES "Attributes"("guid")
);""", "", """CREATE INDEX "Attributes.fk_Attributes_Classes" ON "Attributes"("class");
""", """CREATE INDEX "Attributes.PriceIndex" ON "Attributes"("price");
""", """CREATE INDEX "Nodes.NodePriceIndex" ON "Nodes"("price");
""", """CREATE INDEX "NodeValues.fk_Values_Attributes1" ON "NodeValues"("attr");
""", """CREATE INDEX "NodeValues.fk_Values_Nodes1" ON "NodeValues"("node");
""", """CREATE INDEX "NodeValues.fk_NodeValues_NodeValues1" ON "NodeValues"("bindNode");
""", """CREATE INDEX "NodeValues.fk_NodeValues_NodeValues2" ON "NodeValues"("bindAttr");
""", """CREATE INDEX "NodeValues.indexed_index" ON "NodeValues"("indexed");
""", """CREATE INDEX "NodeValues.NodeValues_value_index" ON "NodeValues"("value");
""", """CREATE INDEX "Links.fk_Links_Classes1" ON "Links"("class");
""", """CREATE INDEX "Links.fk_Links_Classes2" ON "Links"("link");
""", """CREATE INDEX "FullText.fk_FullText_NodeValues1" ON "FullText"("node");
""", """CREATE INDEX "FullText.fk_FullText_NodeValues2" ON "FullText"("attr");
""", """CREATE INDEX "FullText.FullText_Value_Index" ON "FullText"("value");
""", """CREATE INDEX "NodeVersions.fk_NodeVersions_Nodes1" ON "NodeVersions"("node");
""", """CREATE INDEX "NodeVersions.fk_NodeVersions_Classes1" ON "NodeVersions"("class");
""", """CREATE INDEX "fk_Value3D_Attributes1_idx" ON "Value3D"("attr");
""", """CREATE INDEX "fk_Value3D_attr_x0" ON "Value3D"("x0");
""", """CREATE INDEX "fk_Value3D_attr_x1" ON "Value3D"("x1");
""", """CREATE INDEX "fk_Value3D_attr_y0" ON "Value3D"("y0");
""", """CREATE INDEX "fk_Value3D_attr_y1" ON "Value3D"("y1");
""", """CREATE INDEX "fk_Value3D_attr_z0" ON "Value3D"("z0");
""", """CREATE INDEX "fk_Value3D_attr_z1" ON "Value3D"("z1");
""", """CREATE INDEX "fk_Value3D_attr_id" ON "Value3D"("id");
""","", """INSERT INTO "Classes" VALUES('شرکت',0);
""","""INSERT INTO "Classes" VALUES('TimeResearch',0);
""","""INSERT INTO "Classes" VALUES('GeneralDatas',0);
""","""INSERT INTO "Classes" VALUES('Tree',0);
""","""INSERT INTO "Classes" VALUES('General',0);
""","""INSERT INTO "Classes" VALUES('BasketItem',0);
""","""INSERT INTO "Classes" VALUES('Summery',0);
""","""INSERT INTO "Classes" VALUES('GeneralTools',0);
""", """INSERT INTO "Classes" VALUES('TextView',0);
""", """INSERT INTO "Classes" VALUES('Tag',0);
""", """INSERT INTO "Classes" VALUES('GeneralProfile',0);
""", """INSERT INTO "Classes" VALUES('GeneralDetails',0);
""", """INSERT INTO "Classes" VALUES('GeneralTime',0);
""", """INSERT INTO "Classes" VALUES('ClipboardItem',0);
""", """INSERT INTO "Classes" VALUES('EventsTreeView',0);
""", """INSERT INTO "Classes" VALUES('EventLine',0);
""", """INSERT INTO "Classes" VALUES('EventPoint',0);
""", """INSERT INTO "Classes" VALUES('FileManager',0);
""", """INSERT INTO "Classes" VALUES('Garbages',0);
""", """INSERT INTO "Classes" VALUES('TitlesTreeOldData',0);
""", """INSERT INTO "Classes" VALUES('ProfileState',0);
""", """INSERT INTO "Classes" VALUES('Instance',0);
""", """INSERT INTO "Classes" VALUES('QuranAye',0);
""", """INSERT INTO "Classes" VALUES('QuranTranslator',0);
""", """INSERT INTO "Classes" VALUES('QuranWord',0);
""", """INSERT INTO "Classes" VALUES('QuranAyeTranslation',0);
""", """INSERT INTO "Classes" VALUES('QuranTokenFeature',0);
""", """INSERT INTO "Classes" VALUES('QuranSure',0);
""", """INSERT INTO "Classes" VALUES('QuranTokens',0);
""", """INSERT INTO "Classes" VALUES('RecentNodes',0);
""", """INSERT INTO "Classes" VALUES('RepositoryManager',0);
""", """INSERT INTO "Classes" VALUES('Repository',0);
""", """INSERT INTO "Classes" VALUES('StartUpManagerItem',0);
""", """INSERT INTO "Classes" VALUES('FileItem',0);
""", """INSERT INTO "Classes" VALUES('FirstClass',0);
""", """INSERT INTO "Classes" VALUES('Abcd',0);
""", """INSERT INTO "Classes" VALUES('NewClass',0);
""", """INSERT INTO "Classes" VALUES('TimeLine',0);
""", """INSERT INTO "Classes" VALUES('TimeLineItem',0);
""", """INSERT INTO "Classes" VALUES('RootTree',0);
""", """INSERT INTO "Classes" VALUES('لینک',0);
""", """INSERT INTO "Classes" VALUES('انسان',0);
""", """INSERT INTO "Classes" VALUES('FileIndexItem',0);
""", """INSERT INTO "Classes" VALUES('TimeLineRoot',0);
""","", """INSERT INTO "Attributes" VALUES('انسان->templateAttr_line_نام.خانوادگی','templateAttr_line_نام.خانوادگی','انسان',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('انسان->templateAttr_connect_فرزندان','templateAttr_connect_فرزندان','انسان',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('شرکت->templateAttr_date_تاریخ.روزنامه','templateAttr_date_تاریخ.روزنامه','شرکت',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('شرکت->templateAttr_check_زنده.است','templateAttr_check_زنده.است','شرکت',0,NULL,0,4,'::');
""", """INSERT INTO "Attributes" VALUES('Tag->childs','childs','Tag',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('GeneralDatas->iconName','iconName','GeneralDatas',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TextView->tempFile','tempFile','TextView',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('EventPoint->icon','icon','EventPoint',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TimeResearch->EventsTreePlugin_settings','EventsTreePlugin_settings','TimeResearch',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TimeResearch->EventsTreePlugin_tools','EventsTreePlugin_tools','TimeResearch',0,NULL,0,5,'::');
""", """INSERT INTO "Attributes" VALUES('TimeResearch->EventsTreePlugin_create','EventsTreePlugin_create','TimeResearch',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralDatas->description','description','GeneralDatas',0,NULL,0,0,'::(\\w\\w\\w+)::(\\{\\w+-\\w+-\\w+-\\w+-\\w+\\})::');
""", """INSERT INTO "Attributes" VALUES('GeneralDatas->picture','picture','GeneralDatas',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralDatas->files','files','GeneralDatas',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('Tree->brushStyle','brushStyle','Tree',0,NULL,0,15,'::');
""", """INSERT INTO "Attributes" VALUES('Tree->fontStyle','fontStyle','Tree',0,NULL,0,8,'::');
""", """INSERT INTO "Attributes" VALUES('Tree->fontColor','fontColor','Tree',0,NULL,0,9,'::');
""", """INSERT INTO "Attributes" VALUES('Tree->iconName','iconName','Tree',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('General->childs','childs','General',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('General->name','name','General',0,NULL,0,0,'::(\\w\\w\\w+)::');
""", """INSERT INTO "Attributes" VALUES('General->linkTo','linkTo','General',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('General->refereTo','refereTo','General',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('General->combinedNode','combinedNode','General',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('BasketItem->items','items','BasketItem',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('Summery->summeryTemplate','summeryTemplate','Summery',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralTools->tools','tools','GeneralTools',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('TextView->text','text','TextView',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('Tag->tagName','tagName','Tag',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('Tag->tags','tags','Tag',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('GeneralProfile->viewName','viewName','GeneralProfile',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralProfile->views','views','GeneralProfile',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('GeneralDetails->rootFlag','rootFlag','GeneralDetails',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralDetails->invisible','invisible','GeneralDetails',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralDetails->createDate','createDate','GeneralDetails',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralDetails->createTime','createTime','GeneralDetails',0,NULL,0,11,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralDetails->owner','owner','GeneralDetails',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('GeneralDetails->global','global','GeneralDetails',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralDetails->garbage','garbage','GeneralDetails',0,'@bool:1',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralDetails->version','version','GeneralDetails',0,'@uint:1',0,3,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralTime->t','t','GeneralTime',0,'@uint:0',0,3,'::');
""", """INSERT INTO "Attributes" VALUES('GeneralTime->dateFormat','dateFormat','GeneralTime',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('ClipboardItem->items','items','ClipboardItem',0,NULL,0,5,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->fontSize','fontSize','EventsTreeView',0,'@int:9',0,2,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->verticalZoom','verticalZoom','EventsTreeView',0,'@bool:1',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->backColor','backColor','EventsTreeView',0,'@string:#ffffff',0,0,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->guideLine','guideLine','EventsTreeView',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->fontItalic','fontItalic','EventsTreeView',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->direction','direction','EventsTreeView',0,'@int:0',0,2,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->fontFamily','fontFamily','EventsTreeView',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->flagVisible','flagVisible','EventsTreeView',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->fontBold','fontBold','EventsTreeView',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->lastLeft','lastLeft','EventsTreeView',0,'@real:0',0,1,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->lastHeight','lastHeight','EventsTreeView',0,'@real:0',0,1,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->lineOpacity','lineOpacity','EventsTreeView',0,'@bool:1',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->verticalFlags','verticalFlags','EventsTreeView',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->linesHeight','linesHeight','EventsTreeView',0,'@int:4',0,2,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->lastWidth','lastWidth','EventsTreeView',0,'@real:0',0,1,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->dateFormat','dateFormat','EventsTreeView',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->fancyMode','fancyMode','EventsTreeView',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->lastTop','lastTop','EventsTreeView',0,'@real:0',0,1,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->lineSpace','lineSpace','EventsTreeView',0,'@int:35',0,2,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->fillMode','fillMode','EventsTreeView',0,'@bool:1',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventsTreeView->root','root','EventsTreeView',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('EventLine->colors','colors','EventLine',0,NULL,0,6,'::');
""", """INSERT INTO "Attributes" VALUES('EventLine->points','points','EventLine',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('EventLine->guideLine','guideLine','EventLine',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventLine->attachToday','attachToday','EventLine',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventLine->t0Proximate','t0Proximate','EventLine',0,'@int:0',0,2,'::');
""", """INSERT INTO "Attributes" VALUES('EventLine->t1Proximate','t1Proximate','EventLine',0,'@int:0',0,2,'::');
""", """INSERT INTO "Attributes" VALUES('EventLine->lineOpacity','lineOpacity','EventLine',0,'@real:1',0,1,'::');
""", """INSERT INTO "Attributes" VALUES('EventLine->t1','t1','EventLine',0,'@uint:1000000000000000000',0,3,'::');
""", """INSERT INTO "Attributes" VALUES('EventLine->combines','combines','EventLine',0,NULL,0,6,'::');
""", """INSERT INTO "Attributes" VALUES('EventLine->flagVisible','flagVisible','EventLine',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventPoint->guideLine','guideLine','EventPoint',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('EventPoint->pointColor','pointColor','EventPoint',0,NULL,0,9,'::');
""", """INSERT INTO "Attributes" VALUES('FileManager->iconSize','iconSize','FileManager',0,NULL,0,1,'::');
""", """INSERT INTO "Attributes" VALUES('Garbages->noNames','noNames','Garbages',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('Garbages->noConnects','noConnects','Garbages',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('TitlesTreeOldData->actionUrl','actionUrl','TitlesTreeOldData',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TitlesTreeOldData->conceptId','conceptId','TitlesTreeOldData',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TitlesTreeOldData->actionType','actionType','TitlesTreeOldData',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TitlesTreeOldData->additionalData','additionalData','TitlesTreeOldData',0,NULL,0,5,'::');
""", """INSERT INTO "Attributes" VALUES('TitlesTreeOldData->optionsString','optionsString','TitlesTreeOldData',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TitlesTreeOldData->actionName','actionName','TitlesTreeOldData',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TitlesTreeOldData->readonlyStatus','readonlyStatus','TitlesTreeOldData',0,NULL,0,4,'::');
""", """INSERT INTO "Attributes" VALUES('ProfileState->lastTool','lastTool','ProfileState',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('ProfileState->lastView','lastView','ProfileState',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('Instance->instance','instance','Instance',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranAye->text','text','QuranAye',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranAye->number','number','QuranAye',0,NULL,0,3,'::');
""", """INSERT INTO "Attributes" VALUES('QuranAye->sure','sure','QuranAye',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranAye->translations','translations','QuranAye',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('QuranAye->words','words','QuranAye',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('QuranAye->othmanyPageNumber','othmanyPageNumber','QuranAye',0,NULL,0,3,'::');
""", """INSERT INTO "Attributes" VALUES('QuranTranslator->translator','translator','QuranTranslator',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranWord->text','text','QuranWord',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranWord->tokens','tokens','QuranWord',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('QuranWord->number','number','QuranWord',0,NULL,0,3,'::');
""", """INSERT INTO "Attributes" VALUES('QuranWord->aye','aye','QuranWord',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranAyeTranslation->translator','translator','QuranAyeTranslation',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranAyeTranslation->aye','aye','QuranAyeTranslation',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranTokenFeature->type','type','QuranTokenFeature',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranTokenFeature->value','value','QuranTokenFeature',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranSure->sureName','sureName','QuranSure',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranSure->number','number','QuranSure',0,NULL,0,3,'::');
""", """INSERT INTO "Attributes" VALUES('QuranSure->rukuCount','rukuCount','QuranSure',0,'@uint:0',0,3,'::');
""", """INSERT INTO "Attributes" VALUES('QuranSure->nozoolOrder','nozoolOrder','QuranSure',0,NULL,0,3,'::');
""", """INSERT INTO "Attributes" VALUES('QuranSure->nozoolCity','nozoolCity','QuranSure',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranSure->ayat','ayat','QuranSure',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('QuranTokens->number','number','QuranTokens',0,NULL,0,3,'::');
""", """INSERT INTO "Attributes" VALUES('QuranTokens->form','form','QuranTokens',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('QuranTokens->features','features','QuranTokens',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('QuranTokens->word','word','QuranTokens',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('RecentNodes->opened','opened','RecentNodes',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('RecentNodes->modified','modified','RecentNodes',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('RecentNodes->added','added','RecentNodes',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('RepositoryManager->repositories','repositories','RepositoryManager',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('Repository->url','url','Repository',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('Repository->id','id','Repository',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('StartUpManagerItem->lastSession','lastSession','StartUpManagerItem',0,'@bool:0',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('StartUpManagerItem->items','items','StartUpManagerItem',0,NULL,0,5,'::');
""", """INSERT INTO "Attributes" VALUES('FileItem->modify','modify','FileItem',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('FileItem->created','created','FileItem',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('FileItem->url','url','FileItem',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('FileItem->format','format','FileItem',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('FileItem->fileName','fileName','FileItem',0,NULL,0,0,'::(\\w\\w\\w+)::');
""", """INSERT INTO "Attributes" VALUES('FileItem->fileSize','fileSize','FileItem',0,NULL,0,2,'::');
""", """INSERT INTO "Attributes" VALUES('FileItem->added','added','FileItem',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('FirstClass->b','b','FirstClass',4,'@int:6',0,2,'::');
""", """INSERT INTO "Attributes" VALUES('FirstClass->abcd','abcd','FirstClass',4,'@string:Okkey',0,0,'::ardi::');
""", """INSERT INTO "Attributes" VALUES('FirstClass->c1','c1','FirstClass',2,'@bool:1',0,4,'::');
""", """INSERT INTO "Attributes" VALUES('FirstClass->c2','c2','FirstClass',1,NULL,0,1,'::');
""", """INSERT INTO "Attributes" VALUES('FirstClass->c3','c3','FirstClass',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('Abcd->hi','hi','Abcd',0,'@string:done',0,0,'::');
""", """INSERT INTO "Attributes" VALUES('Abcd->Hi','Hi','Abcd',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('NewClass->abcd','abcd','NewClass',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TextView->lastImportDate','lastImportDate','TextView',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('TextView->lastImportTime','lastImportTime','TextView',0,NULL,0,11,'::');
""", """INSERT INTO "Attributes" VALUES('TimeLine->dateFormat','dateFormat','TimeLine',0,'@string:gregorian',0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TimeLineItem->proximate','proximate','TimeLineItem',0,NULL,0,2,'::');
""", """INSERT INTO "Attributes" VALUES('TimeLineItem->parent','parent','TimeLineItem',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('TimeLineItem->x','x','TimeLineItem',2,'@int:0',0,2,'::');
""", """INSERT INTO "Attributes" VALUES('Tree->direction','direction','Tree',0,'@int:2',0,2,'::');
""", """INSERT INTO "Attributes" VALUES('Tree->lastDescriptionState','lastDescriptionState','Tree',0,'@int:0',0,2,'::');
""", """INSERT INTO "Attributes" VALUES('RootTree->defaultFontStyle','defaultFontStyle','RootTree',0,NULL,0,8,'::');
""", """INSERT INTO "Attributes" VALUES('لینک->templateAttr_connect_ارتباط.به','templateAttr_connect_ارتباط.به','لینک',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('انسان->templateAttr_line_نام','templateAttr_line_نام','انسان',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('انسان->templateAttr_files_کتابهای.نوشته.شده','templateAttr_files_کتابهای.نوشته.شده','انسان',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('انسان->templateAttr_date_تاریخ.تولد','templateAttr_date_تاریخ.تولد','انسان',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('انسان->templateAttr_text_ویژگی.های.فردی','templateAttr_text_ویژگی.های.فردی','انسان',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('انسان->templateAttr_line_فامیلی','templateAttr_line_فامیلی','انسان',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('انسان->templateAttr_check_زنده','templateAttr_check_زنده','انسان',0,NULL,0,4,'::');
""", """INSERT INTO "Attributes" VALUES('انسان->templateAttr_connect_اساتید','templateAttr_connect_اساتید','انسان',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('انسان->templateAttr_picture_تصویر','templateAttr_picture_تصویر','انسان',0,NULL,0,7,'::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->format','format','FileIndexItem',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->lastIndexTime','lastIndexTime','FileIndexItem',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->url','url','FileIndexItem',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->node','node','FileIndexItem',8,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->fileName','fileName','FileIndexItem',0,NULL,0,0,'::(\\w\\w\\w+)::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->fileContent','fileContent','FileIndexItem',0,NULL,0,0,'::(\\w\\w\\w+)::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->indexState','indexState','FileIndexItem',0,NULL,0,2,'::');
""", """INSERT INTO "Attributes" VALUES('TimeLineRoot->timeLines','timeLines','TimeLineRoot',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('TimeLine->points','points','TimeLine',8,NULL,0,5,'::(.+)::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->lurl','lurl','FileIndexItem',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->accessed','accessed','FileIndexItem',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->modified','modified','FileIndexItem',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->created','created','FileIndexItem',0,NULL,0,10,'::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->rootPath','rootPath','FileIndexItem',0,NULL,0,0,'::');
""", """INSERT INTO "Attributes" VALUES('FileIndexItem->fileId','fileId','FileIndexItem',0,NULL,0,0,'::');          
            """,""]
        self.conn = sqlite3.connect(dbpath,timeout=300);
        self.db = self.conn.cursor()
        for script in initScripts:
            if len(script)==0:
                self.conn.commit()
            else:
                self.db.execute(script)
        self.conn.commit()
    def closeDb(self):
        self.conn.close()
    def clearDb(self):
        self.db.execute("delete from Nodes;")
        self.db.execute("delete from NodeValues;")
        self.conn.commit()
    def createNode(self):
        node = '{%s}'%(uuid.uuid4());
        self.db.execute("insert into Nodes (`id`,`price`) values ('%s','0');"%node)
#        self.conn.commit()
        return node
    
    def findConditions(self, conditions):
        sql = u"select distinct node from NodeValues where %s"%conditions
        #print sql
        self.db.execute(sql)
        return self.db.fetchall()
      
    
    def findCondition(self, cls, attr, condition):
        return self.findConditions(u"`attr`='%s->%s' and `value` %s"%(cls,attr,condition))
    
    def findMatch(self, cls, attr, match,typ="@string:"):
        matchval = match.replace("'","''")
        return self.findCondition(cls, attr, u"='%s%s'"%(typ,matchval))
    
    def value(self, node, cls, attr,typ="@string:"):
        clsattr = u"%s->%s"%(cls,attr)
        self.db.execute(u"select value from NodeValues where `node`=='%s' and `attr`='%s'"%(node,clsattr))
        results = self.db.fetchall()
        if len(results)==0:
            return None
        else:
            return results[0][0][len(typ):]
        
    
    def setValue(self, node, cls, attr, val,typ="@string:"):
        clsattr = u"%s->%s"%(cls,attr)
        value = val.replace("'","''")
        
#        indexed = u"N/A" 
#        self.db.execute(u"select ftsMethod from Attributes where `class`='%s' and `name`='%s'"%(cls,attr))
#        results = self.db.fetchall()
#        if(len(results)>0):
#            if results[0][0]!=u"::":
#                indexed = results[0][0]
#        sql = u"insert or replace into NodeValues (`node`,`attr`,`value`,`indexed`) values ('%s','%s','%s%s','%s');"%(node,clsattr,typ,value,indexed)
        sql = u"insert or replace into NodeValues (`node`,`attr`,`value`) values ('%s','%s','%s%s');"%(node,clsattr,typ,value)
        #print sql
        self.db.execute(sql)
        #self.conn.commit()

    def deleteConditions(self,condition):        
        self.db.execute(u"delete from NodeValues where %s"%condition)
        #self.conn.commit()
    def delete(self, node):
        self.db.execute(u"delete from Nodes where id='%s'"%node)
        self.db.execute(u"delete from NodeValues where node='%s'"%node)
        #self.conn.commit()
    def commit(self):
        self.conn.commit()