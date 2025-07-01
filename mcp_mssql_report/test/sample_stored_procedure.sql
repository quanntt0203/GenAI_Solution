-- Sample Stored Procedure: sp_GeneratePerformanceReport
-- This is an example stored procedure that demonstrates how to create
-- a performance report with date range and product list parameters

USE [bodb_agentic]  -- Replace with your actual database name
GO

-- Drop procedure if it exists
IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_GeneratePerformanceReport]') AND type in (N'P', N'PC'))
DROP PROCEDURE [dbo].[sp_GeneratePerformanceReport]
GO

CREATE PROCEDURE [dbo].[sp_GeneratePerformanceReport]
    @FromDate DATE,
    @ToDate DATE,
    @ProductList dbo.ProductListType READONLY  -- Assuming you have a user-defined table type
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Sample performance report query
    -- Modify this according to your actual database schema and requirements
    
    SELECT 
        p.ProductName,
        p.ProductID,
        COUNT(o.OrderID) as TotalOrders,
        SUM(od.Quantity) as TotalQuantitySold,
        SUM(od.Quantity * od.UnitPrice) as TotalRevenue,
        AVG(od.UnitPrice) as AverageUnitPrice,
        MIN(o.OrderDate) as FirstOrderDate,
        MAX(o.OrderDate) as LastOrderDate,
        COUNT(DISTINCT o.CustomerID) as UniqueCustomers,
        SUM(od.Quantity * od.UnitPrice) / NULLIF(COUNT(o.OrderID), 0) as RevenuePerOrder
    FROM 
        Products p
        INNER JOIN @ProductList pl ON p.ProductName = pl.ProductName
        LEFT JOIN OrderDetails od ON p.ProductID = od.ProductID
        LEFT JOIN Orders o ON od.OrderID = o.OrderID 
            AND o.OrderDate >= @FromDate 
            AND o.OrderDate <= @ToDate
    GROUP BY 
        p.ProductID, p.ProductName
    ORDER BY 
        TotalRevenue DESC;
        
    -- Additional summary information
    SELECT 
        'SUMMARY' as ReportSection,
        COUNT(DISTINCT p.ProductID) as ProductsAnalyzed,
        @FromDate as ReportStartDate,
        @ToDate as ReportEndDate,
        COUNT(DISTINCT o.OrderID) as TotalOrdersInPeriod,
        SUM(od.Quantity * od.UnitPrice) as TotalRevenueAllProducts
    FROM 
        Products p
        INNER JOIN @ProductList pl ON p.ProductName = pl.ProductName
        LEFT JOIN OrderDetails od ON p.ProductID = od.ProductID
        LEFT JOIN Orders o ON od.OrderID = o.OrderID 
            AND o.OrderDate >= @FromDate 
            AND o.OrderDate <= @ToDate;
            
    RETURN 0;
END
GO

-- Create User-Defined Table Type for Product List (if it doesn't exist)
IF NOT EXISTS (SELECT * FROM sys.types WHERE is_table_type = 1 AND name = 'ProductListType')
BEGIN
    CREATE TYPE [dbo].[ProductListType] AS TABLE(
        [ProductName] [NVARCHAR](255) NOT NULL
    )
END
GO

-- Alternative version that works without user-defined table types
-- This version uses dynamic SQL and is called differently from the Python code

IF EXISTS (SELECT * FROM sys.objects WHERE object_id = OBJECT_ID(N'[dbo].[sp_GeneratePerformanceReportSimple]') AND type in (N'P', N'PC'))
DROP PROCEDURE [dbo].[sp_GeneratePerformanceReportSimple]
GO

CREATE PROCEDURE [dbo].[sp_GeneratePerformanceReportSimple]
    @FromDate DATE,
    @ToDate DATE,
    @ProductNames NVARCHAR(MAX)  -- Comma-separated list of product names
AS
BEGIN
    SET NOCOUNT ON;
    
    -- Create temporary table for product list
    CREATE TABLE #TempProductList (ProductName NVARCHAR(255));
    
    -- Parse comma-separated product names and insert into temp table
    -- This is a simple approach - consider using STRING_SPLIT in SQL Server 2016+
    DECLARE @SQL NVARCHAR(MAX) = '';
    DECLARE @ProductName NVARCHAR(255);
    DECLARE @Pos INT;
    
    SET @ProductNames = @ProductNames + ',';  -- Add trailing comma for parsing
    
    WHILE CHARINDEX(',', @ProductNames) > 0
    BEGIN
        SET @Pos = CHARINDEX(',', @ProductNames);
        SET @ProductName = LTRIM(RTRIM(SUBSTRING(@ProductNames, 1, @Pos - 1)));
        
        IF LEN(@ProductName) > 0
        BEGIN
            INSERT INTO #TempProductList (ProductName) VALUES (@ProductName);
        END
        
        SET @ProductNames = SUBSTRING(@ProductNames, @Pos + 1, LEN(@ProductNames));
    END
    
    -- Generate the performance report
    SELECT 
        p.ProductName,
        p.ProductID,
        COUNT(o.OrderID) as TotalOrders,
        SUM(od.Quantity) as TotalQuantitySold,
        SUM(od.Quantity * od.UnitPrice) as TotalRevenue,
        AVG(od.UnitPrice) as AverageUnitPrice,
        MIN(o.OrderDate) as FirstOrderDate,
        MAX(o.OrderDate) as LastOrderDate,
        COUNT(DISTINCT o.CustomerID) as UniqueCustomers,
        SUM(od.Quantity * od.UnitPrice) / NULLIF(COUNT(o.OrderID), 0) as RevenuePerOrder
    FROM 
        Products p
        INNER JOIN #TempProductList tpl ON p.ProductName = tpl.ProductName
        LEFT JOIN OrderDetails od ON p.ProductID = od.ProductID
        LEFT JOIN Orders o ON od.OrderID = o.OrderID 
            AND o.OrderDate >= @FromDate 
            AND o.OrderDate <= @ToDate
    GROUP BY 
        p.ProductID, p.ProductName
    ORDER BY 
        TotalRevenue DESC;
    
    -- Clean up
    DROP TABLE #TempProductList;
    
    RETURN 0;
END
GO

-- Grant execute permissions (adjust as needed for your security requirements)
-- GRANT EXECUTE ON [dbo].[sp_GeneratePerformanceReport] TO [YourUserRole]
-- GRANT EXECUTE ON [dbo].[sp_GeneratePerformanceReportSimple] TO [YourUserRole]

PRINT 'Performance report stored procedures created successfully!'
PRINT 'Available procedures:'
PRINT '  - sp_GeneratePerformanceReport (uses table-valued parameter)'
PRINT '  - sp_GeneratePerformanceReportSimple (uses comma-separated string)'
