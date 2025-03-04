DELIMITER //
CREATE TRIGGER fastapi.update_study_session_subject
AFTER UPDATE ON fastapi.Subject
FOR EACH ROW
BEGIN
    IF NEW.subject_name <> OLD.subject_name THEN
        UPDATE fastapi.StudySession
        SET subject = NEW.subject_name
        WHERE subject_id = OLD.id;
    END IF;
END //

DELIMITER ;