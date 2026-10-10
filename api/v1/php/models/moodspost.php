<?php
try {
    $SQL_Query = 'INSERT INTO moods VALUES (
        :MoodId, 
        :MoodName,  
        :MoodStatus)';
        
    $SQL_Sentence = $DB_Connector->prepare($SQL_Query);
    $SQL_Sentence->bindParam(':MoodId', $body['MoodId'], PDO::PARAM_INT);
    $SQL_Sentence->bindParam(':MoodName', $body['MoodName'], PDO::PARAM_STR);
    $SQL_Sentence->bindParam(':MoodStatus', $body['MoodStatus'], PDO::PARAM_STR);
    $SQL_Sentence->execute();
    
    if ($SQL_Sentence->rowCount() != 0) {
        $MoodId = $DB_Connector->lastInsertId(); // Get newly created record ID
    } else {
        $MoodId = 'Error: Cannot create new record';
    };
}
catch (PDOException $ex) {
    $MoodId = "Hubo un error!!!!!!!!!!!!";
};
?>