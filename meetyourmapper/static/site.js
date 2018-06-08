const OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
const MAX_AREA_SIZE = 2


var relation_id
var city_name
var message_queue = []

function tag_with_osmid(strings, osm_id) {
	return strings[0] + osm_id + strings[1]
}

function area(bounds) {
	return Math.abs(bounds.maxlat - bounds.minlat) * Math.abs(bounds.maxlon - bounds.minlon)
}

function to_mb(n) { return (n / (1024 * 1024)).toFixed(2) }

function msg(txt, color) {
	$("#messages").empty();
	message_queue.unshift(new Date().toLocaleString() + ': ' + txt);
	if (message_queue.length > 5) message_queue.pop()
	for (i = 0; i < message_queue.length; i++) {
  		$('<div />').text(message_queue[i]).appendTo('#messages');
	}
}

function make_table(data, elem) {
	for (user in data) {
		let u = data[user]
		let f = new Date(u.f)
		let l = new Date(u.l)
		elem.find("tbody:last").append(
			'<tr><td><a href="https://osm.org/user/' +
			user +
			'" target="_blank">' +
			user +
			'</a><td>' +
			u.n +
			'<td>' +
			u.w +
			'<td>' +
			u.r +
			'<td data-order="' + f.getTime() + '">' +
			f.toLocaleDateString() +
			'<td data-order="' + l.getTime() + '">' +
			l.toLocaleDateString())
	}
}

function display_result(data) {
	let table = $("#results")
	make_table(data, table)
	table.show(500).DataTable();
	msg("Done.")
}

function process_download(data) {
	msg(to_mb(data.size) + ' MB downloaded')
	$.ajax("/process/" + relation_id, {
		success: display_result
	})
}


function process_relation_meta(data) {
	let rel = data.elements[0]
	let bounds = rel.bounds
	msg(data.elements[0].tags["name"])
	if (area(bounds) > MAX_AREA_SIZE)
		msg("area is too big")
	else
		msg("getting OSM data")
		$.ajax("/retrieve/" + relation_id, {
			success: process_download
		})
}

function get_relation_meta() {
	relation_id = $("#relation_id").val()
	$.ajax(OVERPASS_API_URL, {
		beforeSend: msg("loading"),
		method: "POST",
		data: tag_with_osmid`[out:json];relation(${ relation_id });out bb meta;`,
		success: process_relation_meta,
	})
}