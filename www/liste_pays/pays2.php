<?php
    include("data.php");
    $nbpays=count($pays);
    $lettre=$_GET['lettre'];

?>
<!DOCTYPE html>
<html>
    <head>
        <title>Pays commencant par A</title>
        <meta charset="UTF-8"> 
		<link rel="stylesheet" type="text/css" href="style.css">
	</head>
	<body>
        <h1>Liste des pays commencant par <?php echo $lettre?>:</h1>
        <div class="paysA">
            <?php for($i=0; $i<$nbpays; $i++) { ?>
                    <?php if($pays[$i][0] == $lettre) { ?>
                        <p><a href="page1.php?num=<?php echo $i; ?>"><?php echo $pays[$i][0]; ?>-<?php echo $pays[$i]; ?></a></p>
                    <?php } ?>
            <?php } ?>
        </div>
        <p><a href="index.php">Retour</a></p>
	</body>
</html>