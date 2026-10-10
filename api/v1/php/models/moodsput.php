<?php
try {
    $SQL_Query = 'UPDATE moods SET
        MoodName = :MoodName, 
        MoodStatus = :MoodStatus 
        WHERE 
        MoodId = :MoodId';
        
    $SQL_Sentence = $DB_Connector->prepare($SQL_Query);
    $SQL_Sentence->bindParam(':MoodId', $body['MoodId'], PDO::PARAM_INT);
    $SQL_Sentence->bindParam(':MoodName', $body['MoodName'], PDO::PARAM_STR);
    $SQL_Sentence->bindParam(':MoodStatus', $body['MoodStatus'], PDO::PARAM_STR);
    $SQL_Sentence->execute();
    
    if ($SQL_Sentence->rowCount() != 0) {
        $newData = $body;
    } else {
        $newData = 'Error: Cannot update record';
    };
}
catch (PDOException $ex) {
    $newData = "Hubo un error!!!!!!!!!!!!";
};
?>