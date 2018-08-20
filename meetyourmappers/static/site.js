const OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
const OVERPASS_ALT_API_URL = "https://overpass.kumi.systems/api/interpreter"
const MAX_AREA_SIZE = 2

var relation_id
var message_queue = []
var totals
var t = $("#results")
var download_flag = false
var overpass_endpoint
var n, s, e, w

function checkBbox(layer) {
   var bounds = layer.getBounds()
   var 
       n = bounds.getNorth(),
       s = bounds.getSouth(),
       e = bounds.getEast(),
       w = bounds.getWest()

   return ((Math.abs(n - s) * Math.abs(e - w)) < 1) 
}

function onDraw(e) {
    editableLayers.clearLayers()
    var layer = e.layer
    var drawResultElem = document.getElementById('drawresult')
    var isValid = checkBbox(layer)
    if (isValid) {
        drawResultElem.innerHTML = 'Bounding Box OK'
    } else {
        drawResultElem.innerHTML = 'Bounding Box too big'
    }
    editableLayers.addLayer(layer)
}


function tag_with_osmid(strings, osm_id) {
	return strings[0] + osm_id + strings[1]
}

function area(bounds) {
	return Math.abs(bounds.maxlat - bounds.minlat) * Math.abs(bounds.maxlon - bounds.minlon)
}

function to_mb(n) { return (n / (1024 * 1024)).toFixed(2) }

function msg(txt, is_error=false) {
	$("#messages").empty()
	message_queue.push(
		{
			"message": new Date().toLocaleString() + ': ' + txt,
			"is_error": is_error
		})
	if (message_queue.length > 5) message_queue.shift()
	for (i = 0; i < message_queue.length; i++) {
		let elem = $('<div />').text(message_queue[i].message)
		if (message_queue[i].is_error) {
			elem.css('color', 'red')
			elem.appendTo('#messages')
			$("#startover").show()
			throw "uh oh"
		}
  		elem.appendTo('#messages')
	}
}

function init() {
	$("#startover").hide()
	$("#submit").prop('disabled', false)
	$("#relation_id").prop('disabled', false)
	$("#save_osmdata").prop('disabled', false)
	$("#use_altserver").prop('disabled', false)
	t.DataTable().clear().destroy()
	t.hide()
	message_queue = []
	// init Leaflet map
	var mymap = L.map('mapid').setView([51.505, -0.09], 13);

	// create the tile layer with correct attribution
	var osmUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png';
	var osmAttrib='Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors';
	var osm = new L.TileLayer(osmUrl, {minZoom: 4, maxZoom: 16, attribution: osmAttrib});        

	// start the map in South-East England
	mymap.setView(new L.LatLng(51.3, 0.7),9);
	mymap.addLayer(osm);

	// add editable layers
	var editableLayers = new L.FeatureGroup();
	mymap.addLayer(editableLayers);

	// add draw control
	var drawControl = new L.Control.Draw({
	    draw: {
	         polyline:false,
	         polygon: false,
	         circle: false,
	         marker: false,
	         circlemarker: false
	     },
	 }).addTo(mymap);

	// add draw event
	mymap.on(L.Draw.Event.CREATED, ondraw);

	msg("Ready")
}

function calculate_magic(user, first, last) {
	let magic = ""
	let firstseen = Math.ceil((new Date() - first) / (1000 * 60 * 60 * 24)) // in days
	let lastseen = Math.ceil((new Date() - last) / (1000 * 60 * 60 * 24)) // in days
	let edits = user.n + user.w + user.r
	let edits_proportion  = (user.n / totals.n) * user.n + (user.w / totals.w) * user.w + (user.r / totals.r) * user.r
	// console.log(firstseen, lastseen, edits, edits_proportion)
	if (lastseen > 365) 
		if (lastseen > 3 * 365) magic = "forgotten"
		else magic = "retired"
	if (edits_proportion > 1) magic += " power"
	else if (edits < 50 && lastseen - firstseen < 90) magic += " mayfly"
	else magic += " "
	if (firstseen < 90) magic = "new"
	magic += " mapper"
	return magic.trim()
}

function make_table(data) {
	for (user in data) {
		let u = data[user]
		let f = new Date(u.f)
		let l = new Date(u.l)
		// console.log(user)
		let m =	calculate_magic(u, f, l)
		let h = '<a href="https://osm.org/user/' + user + '" target="_blank">' + user + '</a>'
		// fixme ugly
		let row = '<tr><td>' + 
			h + 
			'<td>' +
			u.n +
			'<td>' +
			u.w +
			'<td>' +
			u.r +
			'<td data-order="' + f.getTime() + '">' +
			f.toLocaleDateString() +
			'<td data-order="' + l.getTime() + '">' +
			l.toLocaleDateString() + 
			'<td>' +
			m
		t.find("tbody:last").append(row)
	}
}

function display_result(data) {
	totals = data.totals
	totals["days"] = Math.ceil((new Date(totals.l) - new Date(totals.f)) / (1000 * 60 * 60 * 24)) // in days
	make_table(data.users)
	t.show().DataTable({
		dom: 'Bfrtip',
		order: [[5,"desc"]],
		buttons: ['copyHtml5','csvHtml5']
	})
	// console.log(data.file)
	if (download_flag) $("#download").attr("href", data.file).show()
	$("#startover").show()
	msg("Done.")
}

function process_download(data) {
	if (data)
		msg(to_mb(data.size) + ' MB downloaded, processing...')
	else
		msg("loading local data")
	$.ajax("/process?download=" + ($("#save_osmdata").prop("checked") ? 1 : 0), {
		success: display_result,
		error: function(jqXHR, textStatus, errorThrown) { msg("data processing failed", is_error=true) }
	})
}

function process_relation_meta(data) {
	let rel = data.elements[0]
	download_flag = $("#save_osmdata").prop("checked")
	if (!rel)
		msg("no relation found with that ID", is_error=true)
	else if (!("admin_level" in rel.tags || rel.tags.boundary == "local_authority"))
		msg("this does not appear to be an administrative boundary relation", is_error=true)
	else if (parseInt(rel.tags.admin_level) < 6)
		msg("This area is probably too big: admin_level=" + rel.tags.admin_level, is_error=true)
	else {
		let bounds = rel.bounds
		msg(data.elements[0].tags["name"])
		if (area(bounds) > MAX_AREA_SIZE)
			msg("area is too big")
		else
			msg("getting OSM data")
			$.ajax("/get_rel/" + relation_id + "?server=" + overpass_endpoint, {
				success: process_download,
				error: function(jqXHR, textStatus, errorThrown) { msg("data retrieval failed", is_error=true) }
			})
	}
}

function get_relation_meta() {
	relation_id = parseInt($("#relation_id").val())
	if (isNaN(relation_id) || relation_id < 1)
		msg("Please enter a valid relation ID", is_error=true)
	$("#submit").prop('disabled', true)
	$("#relation_id").prop('disabled', true)
	$("#save_osmdata").prop('disabled', true)
	$("#use_altserver").prop('disabled', true)
	overpass_endpoint = $("#use_altserver").prop('checked') ?  OVERPASS_ALT_API_URL : OVERPASS_API_URL
	msg("using Overpass server at " + overpass_endpoint)
	$.ajax(overpass_endpoint, {
		beforeSend: msg("loading"),
		method: "POST",
		data: tag_with_osmid`[out:json];relation(${ relation_id });out bb meta;`,
		success: process_relation_meta,
		error: function() { msg("metadata retrieval failed", is_error=true) }
	})
}

function parse_bbox() {
	// when user defined area of interest using the map to draw a bounding box,
	// we retrieve the data from here and send it on to process_download
	msg("getting OSM data")
	$.ajax("/get_box/?n=" + n + "&s=" + s + "&e=" + e + "&w=" + w + "&server=" + overpass_endpoint, {
		success: process_download,
		error: function(jqXHR, textStatus, errorThrown) { msg("data retrieval failed", is_error=true) }
	})

}

function submit() {
	if (parseInt($("#relation_id").val())) {
		get_relation_meta()
	} else if (n && s && e && w) {
		parse_bbox()
	} else {
		msg("Please supply an OSM relation ID or draw a box on the map.", is_error=true)
	}
}