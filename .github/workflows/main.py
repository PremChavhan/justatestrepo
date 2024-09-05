import boto3
import csv

# Initialize the AWS Audit Manager client
client = boto3.client('auditmanager')

def list_assessment_reports(assessment_id):
    reports = []
    next_token = None
    
    while True:
        if next_token:
            response = client.list_assessment_reports(
                assessmentArn=assessment_id,
                nextToken=next_token
            )
        else:
            response = client.list_assessment_reports(
                assessmentArn=assessment_id
            )
        
        reports.extend(response['assessmentReports'])
        
        next_token = response.get('nextToken')
        if not next_token:
            break
    
    return reports

def get_evidence_by_report(assessment_id, report_id):
    evidence = []
    next_token = None
    
    while True:
        if next_token:
            response = client.get_evidence_by_assessment_report(
                assessmentArn=assessment_id,
                assessmentReportId=report_id,
                nextToken=next_token
            )
        else:
            response = client.get_evidence_by_assessment_report(
                assessmentArn=assessment_id,
                assessmentReportId=report_id
            )
        
        evidence.extend(response['evidenceList'])
        
        next_token = response.get('nextToken')
        if not next_token:
            break
    
    return evidence

def get_latest_failed_evidence(assessment_id):
    latest_evidence = {}
    reports = list_assessment_reports(assessment_id)

    for report in reports:
        evidence_list = get_evidence_by_report(assessment_id, report['assessmentReportId'])
        
        for evidence in evidence_list:
            if evidence['evidenceStatus'] == 'FAILED':  # Filter for failed evidence
                evidence_id = evidence['evidenceId']
                evidence_timestamp = evidence['evidenceTimestamp']
                
                if (evidence_id not in latest_evidence or
                        evidence_timestamp > latest_evidence[evidence_id]['evidenceTimestamp']):
                    latest_evidence[evidence_id] = {
                        'evidenceId': evidence_id,
                        'status': evidence['evidenceStatus'],
                        'description': evidence.get('evidenceDescription', 'N/A'),
                        'evidenceTimestamp': evidence_timestamp
                    }

    return list(latest_evidence.values())

def write_to_csv(evidence_data, filename='latest_failed_evidence.csv'):
    if not evidence_data:
        print("No evidence data available to write to CSV.")
        return

    keys = evidence_data[0].keys()
    with open(filename, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(evidence_data)
    print(f"Data written to {filename}")

# Example usage
assessment_id = 'your-assessment-id'  # Replace with your assessment ID
latest_failed_evidence = get_latest_failed_evidence(assessment_id)
write_to_csv(latest_failed_evidence)
