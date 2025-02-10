-- Query 1: Get contact information along with the application details and the number of applications for each contact
SELECT 
    c.id AS contact_id,
    c.name AS contact_name,
    c.email,
    c.phone,
    c.state,
    a.interest,
    a.reason,
    a.skillsets,
    COUNT(a.id) AS total_applications
FROM 
    contacts c
JOIN 
    applications a ON c.id = a.contact_id
GROUP BY 
    c.id, a.interest, a.reason, a.skillsets
ORDER BY 
    total_applications DESC;

-- Query 2: Get all documents and the associated contact details, including the timestamp of when the document was created
SELECT 
    c.name AS contact_name,
    c.email,
    d.document_name,
    d.document_path,
    d.timestamp AS document_creation_timestamp
FROM 
    application_documents d
JOIN 
    contacts c ON d.contact_id = c.id
WHERE 
    d.timestamp >= '2025-01-01'  -- Filter documents created after January 1, 2025
ORDER BY 
    d.timestamp DESC;

-- UNION Query: Combine the results of the above two queries into a single result set
SELECT 
    c.id AS contact_id,
    c.name AS contact_name,
    c.email,
    c.phone,
    c.state,
    a.interest,
    a.reason,
    a.skillsets,
    COUNT(a.id) AS total_applications,
    NULL AS document_name,
    NULL AS document_path,
    NULL AS document_creation_timestamp
FROM 
    contacts c
JOIN 
    applications a ON c.id = a.contact_id
GROUP BY 
    c.id, a.interest, a.reason, a.skillsets
UNION ALL
SELECT 
    c.id AS contact_id,
    c.name AS contact_name,
    c.email,
    c.phone,
    c.state,
    NULL AS interest,
    NULL AS reason,
    NULL AS skillsets,
    NULL AS total_applications,
    d.document_name,
    d.document_path,
    d.timestamp AS document_creation_timestamp
FROM 
    application_documents d
JOIN 
    contacts c ON d.contact_id = c.id
WHERE 
    d.timestamp >= '2025-01-01'  -- Filter documents created after January 1, 2025
ORDER BY 
    contact_id, document_creation_timestamp DESC;

/*
-- Key Insights:
Contact Information: Shows each contact's basic details like name, email, phone number, and state.
Applications: For each contact, it shows their interest, reason, and skills, along with the number of applications they’ve submitted.
Documents: Lists documents associated with the contact, including the document name, path, and timestamp (showing when the document was created).
Key Benefits of This Query:
Centralized View: You get a consolidated view of both the contact’s applications and associated documents, all in one result set.
Efficient Tracking: It allows you to track how many applications each contact has submitted and the documents they've received, all sorted by timestamps.
Comprehensive Analysis: The COUNT function allows for quick reporting of application volume, and the union of data lets you easily analyze both application and document data side by side. */