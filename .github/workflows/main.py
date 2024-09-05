def list_assessment_reports(assessment_id):
    reports = []
    next_token = None
    
    while True:
        params = {
            'assessmentArn': assessment_id
        }
        if next_token:
            params['nextToken'] = next_token
        
        response = client.list_assessment_reports(**params)
        
        reports.extend(response['assessmentReports'])
        
        next_token = response.get('nextToken')
        if not next_token:
            break
    
    return reports
