
# check if a file exists
def s3_file_exists(s3, bucket, prefix):
    res = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
    return 'Contents' in res


# sdb logging parameters
domain_name = "serratus-batch"

def sdb_log(
        sdb, item_name, name, value,
        region='us-east-1'
    ):
        """
        Insert a single record to simpledb domain.
        PARAMS:
        @item_name: unique string for this record.
        @attributes = [
            {'Name': 'duration', 'Value': str(duration), 'Replace': True},
            {'Name': 'date', 'Value': str(date), 'Replace': True},
        ]
        """
        try:
            status = sdb.put_attributes(
                DomainName=domain_name,
                ItemName=str(item_name),
                Attributes=[{'Name':str(name), 'Value':str(value), 'Replace': True}]
            )
        except Exception as e:
            print("SDB put_attribute error:",str(e),'domain_name',domain_name,'item_name',item_name)
            status = False
        try:
            if status['ResponseMetadata']['HTTPStatusCode'] == 200:
                return True
            else:
                print("SDB log error:",status['ResponseMetadata']['HTTPStatusCode'])
                return False
        except:
            print("SDB status structure error, status:",str(status))
            return False

