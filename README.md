Dự án này thực hiện **so sánh hai hệ quản trị cơ sở dữ liệu (DBMS)**:  
- **Microsoft SQL Server**  
- **PostgreSQL**  

Quá trình thực nghiệm bao gồm:
1. Khởi tạo container cho 2 DBMS bằng Docker.
   
2. Tạo schema cơ sở dữ liệu trên từng DBMS.
   
3. Sinh dữ liệu thử nghiệm.
   
4. Chạy các kịch bản benchmark để đo độ trễ và hiệu năng.
   
5.Cấu trúc file:
├── docker-compose.yml # File khởi tạo 2 DBMS trên Docker
├── schema_postgres.sql # File tạo schema cho PostgreSQL
├── schema_sqlserver.sql # File tạo schema cho SQL Server
├── seed_data.py # Script sinh dữ liệu mẫu cho cả 2 DBMS
├── benchmark.py # Script chạy benchmark đo độ trễ
└── README.md # Tài liệu hướng dẫn

6.Các bước thực hiện:
-Khời động Docker Containers: docker-compose up -d
- Tạo 2 schema cho 2 DBMS :
  PostgreSQL : docker exec -i postgres_db psql -U postgres -d postgres < schema_postgres.sql
  SQLSever : docker exec -i sqlserver_db /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P "yourStrong(!)Password" -d master -i schema_sqlserver.sql
- Sinh dữ liệu : seed_data.py
- Chạy benchmark : python benchmark.py
