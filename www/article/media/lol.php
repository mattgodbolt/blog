<?php
$places = array(
	"Land",
	"Village",
	"World",
	"Universe",
	"City",
	"Hamlet",
	"Warehouse",
	"Conurbation",
	"Town"
	);
$place = $places[array_rand($places)];

$items = array(
	array("Leather", "Leather"),
	array("Furniture", "Furniture"),
	array("Kitchen", "Kitchens"),
	);
$item = $items[array_rand($items)];

$strings = array(
	"{$item[0]} $place",
	"$place of {$item[1]}");

$title = $strings[array_rand($strings)];

?>
<html>
<head><title><?=$title?></title>
</head>
<body>
<h1><?=$title?></h1>

<b>Welcome</b> to <?=$title?>.
</body>
</html>

