const OVERPASS_API_URL = "https://overpass-api.de/api/interpreter"
const MAX_AREA_SIZE = 2

var relation_id
var message_queue = []
var totals

function tag_with_osmid(strings, osm_id) {
	return strings[0] + osm_id + strings[1]
}

function area(bounds) {
	return Math.abs(bounds.maxlat - bounds.minlat) * Math.abs(bounds.maxlon - bounds.minlon)
}

function to_mb(n) { return (n / (1024 * 1024)).toFixed(2) }

function msg(txt, color) {
	$("#messages").empty();
	message_queue.push(new Date().toLocaleString() + ': ' + txt);
	if (message_queue.length > 5) message_queue.shift()
	for (i = 0; i < message_queue.length; i++) {
  		$('<div />').text(message_queue[i]).appendTo('#messages');
	}
}

function calculate_magic(user, first, last) {
	let lastseen = Math.ceil((new Date() - last) / (1000 * 60 * 60 * 24)) // in days
	let active = Math.ceil((last - first) / (1000 * 60 * 60 * 24)) // in days
	let edits = (user.n / totals.n) + (user.w / totals.w) * 3 + (user.r / totals.r) * 5
	return ((active / lastseen * 10) * edits).toFixed(2)
}

function make_table(data, table_elem) {
	for (user in data) {
		let u = data[user]
		let f = new Date(u.f)
		let l = new Date(u.l)
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
		table_elem.find("tbody:last").append(row)
	}
}

function display_result(data) {
	totals = data.totals
	var table = $("#results")
	make_table(data.users, table)
	table.show().DataTable({"order": [[6,"desc"]]})
	$("#startover").show();
	msg("Done.")
}

function process_download(data) {
	if (data)
		msg(to_mb(data.size) + ' MB downloaded')
	else
		msg("loading local data")
	$.ajax("/process", {
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
	$("#submit").prop('disabled', true);
	$("#relation_id").prop('disabled', true);
	relation_id = $("#relation_id").val()
	$.ajax(OVERPASS_API_URL, {
		beforeSend: msg("loading"),
		method: "POST",
		data: tag_with_osmid`[out:json];relation(${ relation_id });out bb meta;`,
		success: process_relation_meta,
	})
}
