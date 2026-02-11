-- 관리자 계정 생성 템플릿
-- <USERNAME>, <PASSWORD>, <ROLE_NAME> 값을 실제 값으로 치환해서 사용

-- 사용자 생성
INSERT INTO ADMIN_USER (admin_id, username, password_hash, status, created_at)
VALUES (ADMIN_USER_SEQ.NEXTVAL, '<USERNAME>', 'plain:<PASSWORD>', 'ACTIVE', SYSTIMESTAMP);

-- 역할 부여 (필요한 만큼 반복)
INSERT INTO ADMIN_USER_ROLE (role_id, admin_id, role_name, created_at)
VALUES (ADMIN_USER_ROLE_SEQ.NEXTVAL,
        (SELECT admin_id FROM ADMIN_USER WHERE username='<USERNAME>'),
        '<ROLE_NAME>',
        SYSTIMESTAMP);
