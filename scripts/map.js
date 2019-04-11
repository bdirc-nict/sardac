/*!
 * SAR Data Analysis Program
 *
 * File name		: map.js
 * Creation date	: March 18, 2019
 * License   	    : GPL v2
 * Copyright (c) 2019 National Institute of Information and Communications Technology
*/ 

/// <reference path="jquery.js" />

//---------------------------------------------------------------------
// Geoserver API
//
// 接続先のGeoserverアドレスを設定する
var g_serverAddress = "";

// GeoserverのREST API設定変数
// typeNameの値を使用するユーザIDに変更して下さい。
var g_hazardSearchUrl = g_serverAddress + "";

//---------------------------------------------------------------------
var map; // Define instance of the Leafet Map Class

var mapMinZoom = 2;
var mapMaxZoom = 20;

var g_visibleLayer = [];

//---------------------------------------------------------------------
// Initialize Base Layers
//
var g_basemapInfo = null;

var baseLayers = {};
var currentBaseLayer = null;
var currentBaseLayerId = null;

//---------------------------------------------------------------------
// Initialize Disaster Layer
//
var g_hazardInfo = null;
var g_aHazardLayerInfo = [];
var g_overlayVisible = true;
var g_overlayOpacity = 0.7;

var g_disasterGroup = new L.layerGroup([]);

//---------------------------------------------------------------------
// Initialize Region information

var g_shapeConfig = {};
var g_execComm = false;

var WGS84 = proj4.defs("WGS84");

var g_areaCP = {
    "北海道": {
        lat: 43.450925,
        lng: 142.866211,
        zoom: 7,
        xmin: 139.334,
        ymin: 41.352,
        xmax: 148.894,
        ymax: 45.557
    },
    "東北": {
        lat: 38.801189,
        lng: 140.723877,
        zoom: 7,
        xmin: 139.165,
        ymin: 36.791,
        xmax: 142.072,
        ymax: 41.556
    },
    "関東": {
        lat: 36.131220,
        lng: 139.268188,
        zoom: 8,
        xmin: 127.841,
        ymin: 20.423,
        xmax: 153.987,
        ymax: 37.155
    },
    "北陸": {
        lat: 36.055761,
        lng: 136.230469,
        zoom: 8,
        xmin: 135.449,
        ymin: 35.344,
        xmax: 139.900,
        ymax: 38.554
    },
    "中部": {
        lat: 35.054732,
        lng: 137.466431,
        zoom: 8,
        xmin: 136.276,
        ymin: 34.572,
        xmax: 139.177,
        ymax: 37.030
    },
    "関西": {
        lat: 34.671617,
        lng: 135.807495,
        zoom: 8,
        xmin: 134.253,
        ymin: 33.433,
        xmax: 136.990,
        ymax: 35.779
    },
    "四国": {
        lat: 33.558562,
        lng: 133.533325,
        zoom: 9,
        xmin: 132.012,
        ymin: 32.703,
        xmax: 134.822,
        ymax: 34.565
    },
    "中国": {
        lat: 34.910710,
        lng: 133.291626,
        zoom: 8,
        xmin: 130.775,
        ymin: 33.713,
        xmax: 134.515,
        ymax: 37.248
    },
    "九州": {
        lat: 32.498180,
        lng: 131.017456,
        zoom: 8,
        xmin: 128.104,
        ymin: 27.019,
        xmax: 132.177,
        ymax: 34.728
    },
    "沖縄": {
        lat: 26.583615,
        lng: 128.078613,
        zoom: 7,
        xmin: 122.934,
        ymin: 24.046,
        xmax: 131.332,
        ymax: 27.886
    }
};

//---------------------------------------------------------------------
// Switch visibility of left menu
//
function moveTab() {
    $("#openTab,#closeTab").toggle();
    if ($("#openTab").is(":visible")) {
        // if show the left menu
        $("#left").show().width(350);
        $("#map, #tabOpener").css("left", 350);
    } else {
        // if not show the left menu
        $("#left").hide().width(0);
        $("#map, #tabOpener").css("left", 0);
    }

    resize();
    map.invalidateSize(true);
}

//---------------------------------------------------------------------
// Processing after read DOM
//
$(function () {
    // Definition of the Map
    mapInit();

    var mapDiv = document.getElementById("map");
    mapDiv.addEventListener("mousemove", HandleEvent, false);

    resize();

    //--- 2018/04/13 ---
    setTimeout(function () {

        //--- 2018/04/17 ---
        $("#openTab,#closeTab").toggle();
        if ($("#openTab").is(":visible")) {
            $("#left").show().width(350);
            $("#map, #tabOpener").css("left", 350);
        }
        resize();
        map.invalidateSize(false);
    }, 100);
});

//*****************************************************************************
// function   : HandleEvent
// description: Handle event for Mouse click
//*****************************************************************************
function HandleEvent(e) {
    var point = L.point(e.offsetX, e.offsetY);
    var ll = map.containerPointToLatLng(point);
    var lat = round(ll.lat, 6);
    var lng = round(ll.lng, 6);
    var str = "" + lat + ", " + lng;
    $("#mousePosition").text(str);
}

//---------------------------------------------------------------------
// Round function about below the decimal point N digit
/**
 * @param  {Number} num  Latitude or Longitude
 * @param  {Number} n    index number
 * @return {Number}      rounded Latitude or Longitude
 */
function round(num, n) {
    var tmp = Math.pow(10, n);
    return Math.round(num * tmp) / tmp;
}

//---------------------------------------------------------------------
// Set up behavior of Accordion menu
//
function setAccordion() {

    $('.layerArea > li > section > h5').click(function (e) {
        if (e.target.tagName == "SPAN") {
            return;
        }
        $(this).toggleClass("active");
        $(this).next("ul").slideToggle();
    });

    $('.layerName > li > section > h6').addClass("active");
    $('.layerName > li > section > ul').hide();
    $('.layerName > li > section > h6').click(function (e) {
        // Control of open or close
        $(this).toggleClass("active");
        $(this).next("ul").slideToggle();
    });
    //---

    $('.layerYear > li > section > h6').addClass("active");
    $('.layerYear > li > section > ul').hide();

    $('.layerYear > li > section > h6').click(function (e) {
        // Control of open or close
        $(this).toggleClass("active");
        $(this).next("ul").slideToggle();
    });

    $('.layerInfos > li > section > h6').click(function (e) {
        // Do not work and return if Input tag is clicked
        if (e.target.tagName == "INPUT") {

            return;
        }

        if (g_aHazardLayerInfo.length > 0) {
            // Process of if right edge is clicked
            if (e.offsetX > 300) {
                var id = -1;
                try {
                    id = $(this).attr("id").substr(11); // --> "hazard_name" + index;
                    id = Number(id);
                } catch (e) {}
                if (id >= 0) {
                    var info = g_aHazardLayerInfo[id];
                    map.fitBounds(info.layer.bbox);
                    return;
                }
            }
        }


        if (e.target.tagName == "P") {

            var check = this.firstChild;
            if (check) {
                check.click();
                check.focus();
            }
            return;
        }

        // Control of open or close
        $(this).toggleClass("active");
        $(this).next("ul").slideToggle();
    });
}


//------------------------------------------------------------------------------
// Layer definition
//
function mapInit() {

    // Definition of the Map Control

    var map_options = {
        crs: L.CRS.EPSG3857,
        minZoom: mapMinZoom,
        maxZoom: mapMaxZoom,
        zoomControl: false,
        zoomsliderControl: true,
    };
    map = L.map('map', map_options);

    L.control.scale({
        imperial: false
    }).addTo(map); // Add to the Scale bar (Metric Unit)

    // Define the Bounding Box of All over Japan
    var corner1 = L.latLng(23.84477, 123.49436);
    var corner2 = L.latLng(47.78299, 153.02561);
    var bounds = L.latLngBounds(corner1, corner2);

    map.fitBounds(bounds);

    //--- Get the Base layer list---
    getBasemapInfo();

    //--- Occurrence year ---
    var today = new Date();
    var year = today.getFullYear();
    for (var i = 2000; i <= year; i++) {
        var opt = $(`<option value="${i}">${i}</option>`);
        $("#disaster_yaer").append(opt);
    }

}

//-----------------------------------------------------------------------------
// Get the Basemap list
//
function getBasemapInfo() {

    $.ajax({
        type: "GET",
        url: "Json/basemap.json",
        cache: false,
        dataType: 'text',
        success: function (json) {
            var info = $.parseJSON(json);
            console.log(info);

            g_basemapInfo = info;
            setupBasemap();
        },
        error: function (e) {
            alert("背景地図情報を取得できませんでした。");
        }
    });
}

//-----------------------------------------------------------------------------
// Add Basemap list
//
function setupBasemap() {

    let obj = null;
    let opt = null;
    let flag = false;

    for (var i = 0; g_basemapInfo && i < g_basemapInfo.length; i++) {
        var info = g_basemapInfo[i];
        
        opt = {};
        opt.attribution = info.maps[0].attribution;
        opt.minZoom = info.maps[0].minZoom;
        opt.maxZoom = info.maps[0].maxZoom;
        opt.minNativeZoom = info.maps[0].minNativeZoom;
        opt.maxNativeZoom = info.maps[0].maxNativeZoom;
        opt.crs = L.CRS.EPSG3857;
        obj = new L.tileLayer(info.maps[0].url, opt);

        baseLayers[info.id] = {
            map: obj,
            name: info.name
        };
        
        if (i == 0) {
            currentBaseLayerId = info.id;
        }

        flag = false;
        if (info.visible) {
            flag = true;
            currentBaseLayer = obj;
        }
        
    }

    //--- Layer Control of the Leaflet ---
    var keys = Object.keys(baseLayers);
    var arr = {};
    for (var i = 0; i < keys.length; i++) {
        var info = baseLayers[keys[i]];
        arr[info.name] = info.map;
    }
    L.control.layers(arr).addTo(map);

    currentBaseLayer.addTo(map);

    //--- Fired when base layer's radio button is changed ---
    map.on("baselayerchange", function (e) {
        var keys = Object.keys(baseLayers);
        for (var i = 0; i < keys.length; i++) {
            var key = keys[i];
            if (e.name == baseLayers[key].name) {
                var str = "opt" + key;
                $("#" + str).click();
                break;
            }
        }
    });
}

//---------------------------------------------------------------------
/**
 * @param  {Object} layer
 * @return {Boolean}
 */
function isShapeLayer(layer) {
    if (!g_aHazardLayerInfo)
        return false;

    var aInfo = g_aHazardLayerInfo;
    for (var i = 0; i < aInfo.length; i++) {
        var info = aInfo[i];
        if (layer == info.mapLayer) {
            if (info.layer.type.toLowerCase() != "raster") {
                return true;
            }
        }
    }

    return false;
}

//---------------------------------------------------------------------
// Removes the search result layer from the map
//
function clearVisibleLayer() {
    for (var i = 0; i < g_visibleLayer.length; i++) {
        map.removeLayer(g_visibleLayer[i]);
    }

    g_hazardInfo = null;

    g_visibleLayer = [];
}

//-----------------------------------------------------------------------------
// Set up Process about location jump if Region name is clicked
//
/**
 * @param  {Object} elem  List element of the region name
 * @param  {String} name  Region name
 */
function setJumpOnClick(elem, name) {

    elem.find('span').click(function (e) {
        e.preventDefault();
        var lat = g_areaCP[name].lat;
        var lng = g_areaCP[name].lng;
        var zoom = g_areaCP[name].zoom;
        map.setView(L.latLng(lat, lng), zoom);
    });
}

//-----------------------------------------------------------------------------
// Set up the WFS layer
//
/**
 * @param  {Object} obj  Layer of the search result
 */
function setupWFSLayer(obj) {

    var layer = obj.layer;

    var defaultParams = {
        service: 'WFS',
        version: '2.0',
        request: 'GetFeature',
        typeName: layer.layerName,
        outputFormat: 'text/javascript',
        format_options: 'callback:getJson',
        SrsName: 'EPSG:4326'
    };
    var params = L.Util.extend(defaultParams);
    var URL = layer.url + L.Util.getParamString(params);
    var myLayer = null;
    var ajax = $.ajax({
        url: URL,
        dataType: 'jsonp',
        jsonpCallback: 'getJson',
        success: function (response) {
            myLayer = L.geoJson(response, {
                style: function (feature) {

                    var opt = g_shapeConfig["polygon"];
                    return opt;
                }
            });
            obj.mapLayer = myLayer;

            var input = obj.checkBox;
            $(input).removeAttr('disabled');
        }
    });

}

//-----------------------------------------------------------------------------
// Get the Disaster layer information
//
function getHazardInfo() {

    if (g_execComm) {
        return; // connecting
    }
    g_execComm = true;

    var bbox_min_x = $("#bbox_min_x").val();
    var bbox_min_y = $("#bbox_min_y").val();
    var bbox_max_x = $("#bbox_max_x").val();
    var bbox_max_y = $("#bbox_max_y").val();

    var searchText = $("#disaster_name").val();
    var filterArea = $("#disaster_area option:selected").html();
    var fiscalYear = $("#disaster_yaer option:selected").html();
    if (fiscalYear.indexOf("----") === 0) {
        fiscalYear = 0;
    } else {
        fiscalYear = Number(fiscalYear);
    }

    // Base url of the Geoserver REST API
    var url = g_hazardSearchUrl;

    if (bbox_min_x.length > 0 && bbox_min_y.length > 0 &&
        bbox_max_x.length > 0 && bbox_max_y.length > 0) {
        url += ("&bbox=" + bbox_min_x + "," + bbox_min_y + "," + bbox_max_x + "," + bbox_max_y);
    }

    if ((searchText && searchText.length > 0) ||
        filterArea.indexOf("----") !== 0 || fiscalYear > 0) {

        url += "&viewparams=";
        if (searchText && searchText.length > 0) {
            url += ("disasterName:" + searchText + ";");
        }
        if (filterArea.indexOf("----") !== 0) {
            var areaId = $("#disaster_area option:selected").attr("value");
            if (areaId > 0) {
                url += ("areaId:" + areaId) + ";";
            }
        }
        if (fiscalYear > 0) {
            var fromStr = "" + fiscalYear + "-01-01";
            var toStr = "" + fiscalYear + "-12-31";

            url += ("obsDateFrom:" + fromStr + ";");
            url += ("obsDateTo:" + toStr + ";");
        }
    }

    var ptime_start = new Date().getTime();
    var ptime_end = null;

    $.ajax({
        type: "GET",
        url: url,
        cache: false,
        dataType: 'text',
        success: function (json) {
            ptime_end = new Date().getTime() - ptime_start;
            console.log(ptime_end);
            var info = $.parseJSON(json);
            console.log(info);

            g_hazardInfo = parseHazardInfo(info);
        },
        error: function (e) {
            g_hazardInfo = null;
            alert("災害レイヤ情報を取得できませんでした。");
        }
    }).always(function (data, textStatus, errorThrown) {
        g_execComm = false;
        if (g_hazardInfo) {
            searchDisasterInfo(g_hazardInfo);
        }
    });
}

//---------------------------------------------------------------------
// Get the bounding box of Raster layer
//
/**
 * @param  {Object} geometry  Coordinates of the raster layer
 * @return {Object}           Bounding box of the raster layer
 */

function getBBox(geometry) {

    var bounds = null;
    if (geometry.coordinates && geometry.coordinates.length > 0) {
        var coords = geometry.coordinates[0];
        if (coords && coords.length > 2) {
            var c1 = coords[0];
            var c2 = coords[2];
            bounds = L.latLngBounds(L.latLng(c1[1], c1[0]), L.latLng(c2[1], c2[0]));
        }
    }
    return bounds;
}

//-----------------------------------------------------------------------------
// Parse Hazard information
//
/**
 * @param  {Object} json  Parse result of the Geoserver REST API
 * @return {Array}        Disaster layers list
 */
function parseHazardInfo(json) {

    var features = json.features;
    for (var i = 0; i < features.length; i++) {
        features[i].index = i;
    }

    features.sort(function (a, b) {

        var ca = g_areaList[a.properties.area];
        var cb = g_areaList[b.properties.area];
        if (ca == cb) {

            var ai = a.properties.disaster_id;
            var bi = b.properties.disaster_id;
            if (ai == bi) {
                var ai2 = a.properties.data_type_id;
                var bi2 = b.properties.data_type_id;
                if (ai2 == bi2) {
                    var ai3 = a.index;
                    var bi3 = b.index;
                    ai = ai3;
                    bi = bi3;
                } else {
                    ai = ai2;
                    bi = bi2;
                }
            }
            return (ai - bi);
        }
        return (ca - cb);
    });

    var wi = 0;
    var paInfo = [];
    var obj = null;
    var arr = null;
    var prevId = -1;
    var info = null;
    var prop = null;

    while (wi < features.length) {

        info = features[wi];
        prop = info.properties;
        if (prevId != prop.disaster_id) {
            if (arr && arr.length > 0) {
                obj = {};
                obj.title = arr[0].disaster_name;
                obj.area = arr[0].area;
                obj.layers = arr;
                paInfo.push(obj);
            }
            arr = [];
            prevId = prop.disaster_id;
        }
        prop.bbox = getBBox(info.geometry);
        prop.id = info.id;
        prop.index = info.index;
        arr.push(prop);
        wi += 1;

        if (wi >= features.length) {
            if (arr && arr.length > 0) {
                obj = {};
                obj.title = arr[0].disaster_name;
                obj.area = arr[0].area;
                obj.layers = arr;
                paInfo.push(obj);
            }
            break;
        }
    }

    return paInfo;
}

//-----------------------------------------------------------------------------
/**
 * @param   {String} str   Disaster region name
 * @return  {String} str2  Replaced disastser region name
 */
function replaceParentheses(str) {
    var str1 = str.replace(/\(/g, "（");
    var str2 = str1.replace(/\)/g, "）");
    return str2;
}

//-----------------------------------------------------------------------------
// Search Disaster information
//
var g_areaList = {};
g_areaList["北海道"] = 0;
g_areaList["東北"] = 1;
g_areaList["関東"] = 2;
g_areaList["北陸"] = 3;
g_areaList["中部"] = 4;
g_areaList["関西"] = 5;
g_areaList["四国"] = 6;
g_areaList["中国"] = 7;
g_areaList["九州"] = 8;
g_areaList["沖縄"] = 9;

/**
 * @param  {Array}  aInfo  Parsed disaster layers array
 */
function searchDisasterInfo(aInfo) {

    clearVisibleLayer();
    removeAllChildren("hazardList");
    g_selectedLayer = [];

    var searchText = $("#disaster_name").val();
    var filterArea = $("#disaster_area option:selected").html();
    var fiscalYear = $("#disaster_yaer option:selected").html();
    if (fiscalYear.indexOf("----") === 0) {
        fiscalYear = 0;
    } else {
        fiscalYear = Number(fiscalYear);
    }

    var windex = 0;
    var arr = [];

    for (var i = 0; i < aInfo.length; i++) {
        var info = aInfo[i];
        if (searchText.length > 0) {
            if (info.title.indexOf(searchText) < 0) {
                continue;
            }
        }
        if (filterArea.indexOf("----") !== 0) {
            if (info.area.indexOf(filterArea) < 0) {
                continue;
            }
        }
        var aLayer = info.layers;
        for (var j = 0; j < aLayer.length; j++) {
            var layer = aLayer[j];
            if (searchText.length > 0) {
                if (info.title.indexOf(searchText) < 0) {
                    if (layer.title.indexOf(searchText) < 0) {
                        continue;
                    }
                }
            }

            var obj = {
                title: info.title,
                area: info.area,
                layer: layer,
                mapLayer: null
            };

            var layerNo = windex;
            windex += 1;

            if (layer.type.indexOf("raster") >= 0) {
                if (layer.url.indexOf("/wms") >= 0) {
                    obj.mapLayer = L.tileLayer.wms(layer.url, {
                        layers: layer.layer_nName,
                        format: 'image/png',
                        transparent: true,
                        zIndex: 20 + layerNo,
                        opacity: g_overlayOpacity
                    });
                } else if (layer.url.indexOf("service/wmts") >= 0 ||
                    layer.type.toLowerCase() == "diffraster") {
                    var opt = {
                        layer: layer.layer_name,
                        style: "normal",
                        tilematrixSet: "EPSG:900913",
                        zIndex: 20 + layerNo,
                        format: "image/png"
                    };
                    if (layer.bbox) {
                        opt.bounds = layer.bbox;
                    }
                    obj.mapLayer = new L.TileLayer.WMTS(layer.url, opt);
                } else {
                    // TMS (not via Geoserver)
                    var opt = {
                        tms: true,
                        opacity: g_overlayOpacity,
                        zIndex: 20 + layerNo,
                        format: "image/png"
                    };
                    if (layer.bbox) {
                        opt.bounds = layer.bbox;
                    }
                    obj.mapLayer = L.tileLayer(layer.url, opt);
                }
            }
            else if (layer.type.toLowerCase() == "shapefile" || layer.type.toLowerCase() == "diffraster") {
                if (layer.url.indexOf("service/wmts") >= 0) {
                    var opt = {
                        layer: layer.layer_name,
                        style: "normal",
                        tilematrixSet: "EPSG:900913",
                        zIndex: 100 + layerNo,
                        format: "image/png"
                    };
                    if (layer.bbox) {
                        opt.bounds = layer.bbox;
                    }
                    obj.mapLayer = new L.TileLayer.WMTS(layer.url, opt);
                }
            } else if (layer.type.toLowerCase() == "wfs") {
                setupWFSLayer(obj);
            }
            arr.push(obj);

        }
    }

    // Set up the Search result tab
    var hazardList = $("#hazardList");

    var prevAreaUl = null;

    for (var i = 0; i < arr.length; i++) {
        var info = arr[i];
        var areaName = info.area;
        var title = replaceParentheses(info.title);
        var layer = info.layer;
        var yy = info.layer.obs_date.split("/")[0];
        var id = "hazard_ul" + i;
        var wid = "hazard_name" + i;
        var accordionLayerInfo = "<li><ul id='" + id + "' class='accordion_ul layerInfos'><li><section><h6></h6><ul></ul></section></li></ul></li>";

        //--- Region name ---
        var str = "hazard_" + areaName;
        var areaUl = document.getElementById(str);

        if (!areaUl) {
            var areaLi = $(`<li><section><h5><span>${title}</span></h5><ul id="${str}"></ul></section></li>`);
            hazardList.append(areaLi);
            setJumpOnClick(areaLi, areaName);
            areaUl = $("#" + str);
            prevAreaUl = areaUl;
        } else {
            areaUl = prevAreaUl;
        }
        //--- Disaster name ---
        var accordionTitle;
        if (!areaUl.is(":contains(" + areaName + ")")) {
            // Add layer name to accordion if nothing the "title" layer
            accordionTitle = "<li><ul class='accordion_ul layerName'><li><section><h6>" + areaName + "</h6><ul id='" + layer.disaster_id + "'></ul></section></li></ul></li>"; //--- 2018/05/14 ---
            areaUl.append(accordionTitle);
            areaTitleUl = $("#" + layer.disaster_id);
        }
        var yearTitle;
        if (!areaTitleUl.is(":contains(" + yy + ")")) {
            yearTitle = "<li><ul class='accordion_ul layerYear'><li><section><h6>" + yy + "</h6><ul id='year_" + yy + "'></ul></section></li></ul></li>";
            areaTitleUl.append(yearTitle);
        }
        var yearTitleUl = $("#" + "year_" + yy);

        yearTitleUl.append(accordionLayerInfo);

        var list = document.createElement('li');
        $(list).addClass('list block');

        if (layer.type.toLowerCase() == "shapefile" || layer.type.toLowerCase() == "wfs") {
            $(list).append("<div>" + JSON.stringify(layer, null, "\t") + "</div>");
        } else {
            $(list).append("<div>" + JSON.stringify(layer, null, "\t") + "</div>");
        }

        var ul = $("#" + id + " ul");
        ul.append(list);

        var input = document.createElement('input');
        $(input).attr("type", "checkbox").attr("id", 'overlayLayer' + i).attr("name", "layers").attr("value", i);
        $("#" + id + " h6").addClass("non_select").attr("id", wid).append(input).append("<p class='layerTitle'>" + info.layer.title + "</p>"); // --> レイヤ名

        initCheckBox(input, i);
    }

    var count = 0;
    for (var i = 0; i < arr.length; i++) {
        if (arr[i].layer.type.toLowerCase() == "raster" ||
            arr[i].layer.type.toLowerCase() == "wmts" ||
            arr[i].layer.type.toLowerCase() == "wms") {
            count += 1;
        }
    }
    $("#visibleLayers").text(count);

    g_aHazardLayerInfo = arr;

    //------------------------------------------------------------------
    // Create Method of switch layer if layer clicked
    /**
     * @param  {Object} input  Input element of the disaster name 
     * @param  {Number} index  Index number of disaster layers
     */
    function initCheckBox(input, index) {
        input.onchange = function (s) {
            if (s == null) {
                return;
            }

            var mapLayer = g_aHazardLayerInfo[index].mapLayer;
            if (this.checked) {
                $(input).parent().addClass("select");

                try {
                    if (mapLayer.setOpacity) {
                        mapLayer.setOpacity(g_overlayOpacity);
                    } else {
                        //--- Vector Layer ---
                        var style = {
                            opacity: g_overlayOpacity
                        };
                        mapLayer.setStyle(style);
                    }
                    if (g_overlayVisible || isShapeLayer(mapLayer)) {
                        map.addLayer(mapLayer);
                    }
                    g_visibleLayer.push(mapLayer);

                } catch (e) {};

            } else {
                $(input).parent().removeClass("select");

                map.removeLayer(mapLayer);
                var wi = g_visibleLayer.indexOf(mapLayer);
                if (wi >= 0) {
                    g_visibleLayer.splice(wi, 1);
                }
            }

        };
    };
    //------------------------------------------------------------------

    // Set Accordion menu
    setAccordion();

}

//---------------------------------------------------------------------
// Removing all children from an element
//
/**
 * @param  {String} id  Element name of the search result
 */
function removeAllChildren(id) {
    var element = document.getElementById(id);
    while (element.firstChild) {
        element.removeChild(element.firstChild);
    }
}
