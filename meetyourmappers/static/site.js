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
			elem.css('color', 'red');
			elem.appendTo('#messages')
			$("#startover").show()
			throw "uh oh"
		}
  		elem.appendTo('#messages')
	}
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

function make_table(data, table_elem) {
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
		table_elem.find("tbody:last").append(row)
	}
}

function display_result(data) {
	totals = data.totals
	totals["days"] = Math.ceil((new Date(totals.l) - new Date(totals.f)) / (1000 * 60 * 60 * 24)) // in days
	var table = $("#results")
	make_table(data.users, table)
	table.show().DataTable({
		"order": [[6,"desc"]],
	})
	$("#startover").show()
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
	if (!rel)
		msg("no relation found with that ID", is_error=true)
	else if (!("admin_level" in rel.tags))
		msg("this is not a boundary relation", is_error=true)
	else if (parseInt(rel.tags.admin_level) < 6)
		msg("This area is probably too big: admin_level=" + rel.tags.admin_level, is_error=true)
	else {
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
}

function get_relation_meta() {
	$("#submit").prop('disabled', true)
	$("#relation_id").prop('disabled', true)
	relation_id = $("#relation_id").val()
	$.ajax(OVERPASS_API_URL, {
		beforeSend: msg("loading"),
		method: "POST",
		data: tag_with_osmid`[out:json];relation(${ relation_id });out bb meta;`,
		success: process_relation_meta,
	})
}
