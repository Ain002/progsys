<?php
    include("data.php");
    $nbpays=$_GET['num'];
?>
<!DOCTYPE html>
<html>
    <head>
        <title>Exemple PHP</title>
        <meta charset="UTF-8"> 
		<link rel="stylesheet" type="text/css" href="style.css">
	</head>
	<body>
        <h1>Name bro!!</h1>
        <ul>
            <li><h3><?php echo $pays[$nbpays]; ?></h3></li>
        </ul>
        <p><a href="index.php">Retour</a></p>
	</body>
</html>