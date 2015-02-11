function updatePostingTime(id, time) {
  if (!document)
    return;
  if (!document.getElementById)
    return;

  var span = document.getElementById(id);
  if (!span)
    return;

  // time in the form yyyy-mm-ddThh:mm:ssZ.
  var year = time.substring(0, 4);
  var month = Number(time.substring(5, 7)) - 1;
  var day = time.substring(8, 10);
  var hour = time.substring(11, 13);
  var minute = time.substring(14, 16);
  var second = time.substring(17, 19);
  var then_ms_utc = Date.UTC(year, month, day, hour, minute, second);
  var now_ms_utc = new Date().getTime();

  var diff_min = (now_ms_utc - then_ms_utc) / 1000 / 60;
  var diff_desc;

  if (diff_min < 3)          diff_desc = "just a few minutes";
  else if (diff_min < 60)
    diff_desc = "about " + Math.round(diff_min.toString()) + " minutes";
  else if (diff_min < 65)    diff_desc = "about an hour";
  else if (diff_min < 90)    diff_desc = "just over an hour";
  else if (diff_min < 120)   diff_desc = "nearly two hours";
  else if (diff_min < 125)   diff_desc = "about two hours";
  else if (diff_min < 150)   diff_desc = "just over two hours";
  else if (diff_min < 180)   diff_desc = "nearly three hours";
  else if (diff_min < 185)   diff_desc = "about three hours";
  else if (diff_min < 210)   diff_desc = "just over three hours";
  else if (diff_min < 240)   diff_desc = "nearly four hours";
  else if (diff_min < 245)   diff_desc = "about four hours";
  else if (diff_min < 270)   diff_desc = "just over four hours";
  else if (diff_min < 24*60)
    diff_desc = "about " + Math.round(diff_min / 60).toString() + " hours";
  else if (diff_min < 37*60) diff_desc = "about a day";
  else if (diff_min < 6*24*60)
    diff_desc = "about " + Math.round(diff_min / 60 / 24).toString() + " days";
  else if (diff_min < 11*24*60)
    diff_desc = "about a week";
  else if (diff_min < 5*7*24*60)
    diff_desc = "about " + Math.round(diff_min / 60 / 24 / 7).toString() +
      " weeks";
  else
    return;  // Nothing useful to say.

  while (span.hasChildNodes())
    span.removeChild(span.firstChild);

  span.appendChild(document.createTextNode("Posted " + diff_desc + " ago."));
  span.title = "Posted at " + time;
}
