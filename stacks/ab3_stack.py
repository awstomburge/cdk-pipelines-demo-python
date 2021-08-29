from aws_cdk import core as cdk
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_elasticloadbalancingv2 as elb
import aws_cdk.aws_rds as rds
import aws_cdk.aws_autoscaling as asg
import aws_cdk.aws_cloudwatch  as cw 

class Ab3Stack(cdk.Stack):

    def __init__(self, scope: cdk.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        # VPC 
        self.vpc = ec2.CfnVPC(self,
            id='VPC',
            cidr_block='172.31.0.0/16',
            enable_dns_hostnames=True,
            enable_dns_support=True,
            tags=[{"key":"Name", "value":"VPC"}]
        )
        
        # Public Subnets
        self.public_subnet1 = ec2.CfnSubnet(self,
            id='Public Subnet APP WEB 1',
            cidr_block='172.31.0.0/19',
            vpc_id=self.vpc.ref,
            availability_zone=cdk.Fn.select(0, cdk.Fn.get_azs()),
            map_public_ip_on_launch=True,
            tags=[{"key":"Name", "value":"Public Subnet APP WEB 1"}]
        )

        self.public_subnet2 = ec2.CfnSubnet(self,
            id='Public Subnet APP WEB 2',
            cidr_block='172.31.32.0/19',
            vpc_id=self.vpc.ref,
            availability_zone=cdk.Fn.select(1, cdk.Fn.get_azs()),
            map_public_ip_on_launch=True,
            tags=[{"key":"Name", "value":"Public Subnet APP WEB 2"}]
        )

        # Private Subnets
        self.private_subnet1 = ec2.CfnSubnet(self,
            id='Private Subnet DB 1',
            cidr_block='172.31.64.0/19',
            vpc_id=self.vpc.ref,
            availability_zone=cdk.Fn.select(0, cdk.Fn.get_azs()),
            map_public_ip_on_launch=False,
            tags=[{"key":"Name", "value":"Private Subnet DB 1"}]
        )

        self.private_subnet2 = ec2.CfnSubnet(self,
            id='Private Subnet DB 2',
            cidr_block='172.31.96.0/19',
            vpc_id=self.vpc.ref,
            availability_zone=cdk.Fn.select(1, cdk.Fn.get_azs()),
            map_public_ip_on_launch=False,
            tags=[{"key":"Name", "value":"Private Subnet DB 2"}]
        )

        # Internet Gateway
        self.internet_gateway = ec2.CfnInternetGateway(self,
            id='IGW',
            tags=[{"key":"Name", "value":"Internet Gateway"}]
        )

        self.internet_gateway_attach = ec2.CfnVPCGatewayAttachment(self,
            id='IGW Attach',
            internet_gateway_id=self.internet_gateway.ref,
            vpc_id=self.vpc.ref
        )

        # Elastic IPs
        self.elastic_ip_1 = ec2.CfnEIP(self,
            id='Elastic IP 1',
            tags=[{"key":"Name", "value":"Elastic IP 1"}]
        )

        self.elastic_ip_2 = ec2.CfnEIP(self,
            id='Elastic IP 2',
            tags=[{"key":"Name", "value":"Elastic IP 2"}]
        )

        # NAT Gateways
        self.nat_gateway_1 = ec2.CfnNatGateway(self,
            id='NAT Gateway 1',
            allocation_id=self.elastic_ip_1.attr_allocation_id,
            connectivity_type='public',
            subnet_id=self.public_subnet1.ref,
            tags=[{"key":"Name", "value":"NAT Gateway 1"}]
        )

        self.nat_gateway_1.add_depends_on(self.elastic_ip_1)

        self.nat_gateway_2 = ec2.CfnNatGateway(self,
            id='NAT Gateway 2',
            allocation_id=self.elastic_ip_2.attr_allocation_id,
            connectivity_type='public',
            subnet_id=self.public_subnet2.ref,
            tags=[{"key":"Name", "value":"NAT Gateway 2"}]
        )

        self.nat_gateway_2.add_depends_on(self.elastic_ip_2)

        # Route Tables
        self.route_table_public_subnet_1 = ec2.CfnRouteTable(self,
            id='Route Table Public Subnet 1',
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"Route Table Public Subnet 1"}]
        )

        self.route_table_public_subnet_2 = ec2.CfnRouteTable(self,
            id='Route Table Public Subnet 2',
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"Route Table Public Subnet 2"}]
        )

        self.route_table_private_subnet_1 = ec2.CfnRouteTable(self,
            id='Route Table Private Subnet 1',
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"Route Table Private Subnet 1"}]
        )

        self.route_table_private_subnet_2 = ec2.CfnRouteTable(self,
            id='Route Table Private Subnet 2',
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"Route Table Private Subnet 2"}]
        )

        self.route_nat_gw_1 = ec2.CfnRoute(self,
            id='Route NAT GW 1',
            destination_cidr_block='0.0.0.0/0',
            nat_gateway_id=self.nat_gateway_1.ref,
            route_table_id=self.route_table_private_subnet_1.ref
        )

        self.route_nat_gw_2 = ec2.CfnRoute(self,
            id='Route NAT GW 2',
            destination_cidr_block='0.0.0.0/0',
            nat_gateway_id=self.nat_gateway_2.ref,
            route_table_id=self.route_table_private_subnet_2.ref
        )

        self.route_internet_gateway_1 = ec2.CfnRoute(self,
            id='Route IGW 1',
            destination_cidr_block='0.0.0.0/0',
            gateway_id=self.internet_gateway.ref,
            route_table_id=self.route_table_public_subnet_1.ref
        )

        self.route_internet_gateway_2 = ec2.CfnRoute(self,
            id='Route IGW 2',
            destination_cidr_block='0.0.0.0/0',
            gateway_id=self.internet_gateway.ref,
            route_table_id=self.route_table_public_subnet_2.ref
        )

        # Public Subnet Associations
        self.public_subnet_assoc_1 = ec2.CfnSubnetRouteTableAssociation(self,
            id='Public Subnet Assoc 1',
            route_table_id=self.route_table_public_subnet_1.ref,
            subnet_id=self.public_subnet1.ref
        )

        self.public_subnet_assoc_2 = ec2.CfnSubnetRouteTableAssociation(self,
            id='Public Subnet Assoc 2',
            route_table_id=self.route_table_public_subnet_2.ref,
            subnet_id=self.public_subnet2.ref
        )

        # Private Subnet Associations
        self.private_subnet_assoc_1 = ec2.CfnSubnetRouteTableAssociation(self,
            id='Private Subnet Assoc 1',
            route_table_id=self.route_table_private_subnet_1.ref,
            subnet_id=self.private_subnet1.ref
        )
        
        self.private_subnet_assoc_2 = ec2.CfnSubnetRouteTableAssociation(self,
            id='Private Subnet Assoc 2',
            route_table_id=self.route_table_private_subnet_2.ref,
            subnet_id=self.private_subnet2.ref
        )

        # Elastic Load Balancer Security Group
        self.elastic_lb_security_group = ec2.CfnSecurityGroup(self,
            id='ELB Security Group',
            group_description='ELB Security Group',
            group_name='ELB Security Group',
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"Elastic LB SG"}]
        )

        self.elb_http_rule = ec2.CfnSecurityGroupIngress(self,
            id='ELB http Rule',
            ip_protocol='tcp',
            from_port=80,
            to_port=80,
            cidr_ip='0.0.0.0/0',
            group_id=self.elastic_lb_security_group.ref
        )

        self.elb_https_rule = ec2.CfnSecurityGroupIngress(self,
            id='ELB https Rule',
            ip_protocol='tcp',
            from_port=443,
            to_port=443,
            cidr_ip='0.0.0.0/0',
            group_id=self.elastic_lb_security_group.ref
        )

        # EC2 Security Group
        self.ec2_security_group = ec2.CfnSecurityGroup(self,
            id='EC2 Security Group',
            group_description='EC2 Security Group',
            group_name='EC2 Security Group',
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"EC2 SG"}]
        )


        self.ec2_http_rule = ec2.CfnSecurityGroupIngress(self,
            id='EC2 http Rule',
            ip_protocol='tcp',
            from_port=80,
            to_port=80,
            group_id=self.ec2_security_group.ref,
            source_security_group_id=self.elastic_lb_security_group.ref
        )

        self.ec2_https_rule = ec2.CfnSecurityGroupIngress(self,
            id='EC2 https Rule',
            ip_protocol='tcp',
            from_port=443,
            to_port=443,
            group_id=self.ec2_security_group.ref,
            source_security_group_id=self.elastic_lb_security_group.ref
        )

        # DB Load Balancer Security Group
        self.db_security_group = ec2.CfnSecurityGroup(self,
            id='DB Security Group',
            group_description='DB Security Group',
            group_name='DB Security Group',
            vpc_id=self.vpc.ref,
            tags=[{"key":"Name", "value":"DB SG"}]
        )

        self.db_port_rule = ec2.CfnSecurityGroupIngress(self,
            id='DB Port Rule',
            ip_protocol='tcp',
            from_port=3306,
            to_port=3306,
            group_id=self.db_security_group.ref,
            source_security_group_id=self.ec2_security_group.ref
        )

        # Aplication Load Balancer
        self.elastic_load_balancer = elb.CfnLoadBalancer(self,
            id='Elastic Load Balancer',
            ip_address_type='ipv4',
            load_balancer_attributes=[
                elb.CfnLoadBalancer.LoadBalancerAttributeProperty(
                    key='idle_timeout.timeout_seconds',
                    value='60'
                )
            ],
            name='Elastic-Load-Balancer',
            scheme='internet-facing',
            security_groups=[self.elastic_lb_security_group.ref],
            subnets=[
                self.public_subnet1.ref,
                self.public_subnet2.ref
            ],
            type='application',
            tags=[{"key":"Name", "value":"Elastic Load Balancer"}]
        )

        self.elb_target_group = elb.CfnTargetGroup(self,
            id='ELB Target Group',
            name='ELB-Target-Group',
            port=80,
            protocol='HTTP',
            vpc_id=self.vpc.ref,
            target_group_attributes=[
                elb.CfnTargetGroup.TargetGroupAttributeProperty(
                    key='stickiness.lb_cookie.duration_seconds',
                    value='86400'
                ),
                elb.CfnTargetGroup.TargetGroupAttributeProperty(
                    key='stickiness.enabled',
                    value='true'
                ),
                elb.CfnTargetGroup.TargetGroupAttributeProperty(
                    key='stickiness.type',
                    value='lb_cookie'
                ),
            ]
        )

        self.elb_listener = elb.CfnListener(self,
            id='ELB Listener',
            default_actions=[{ "type" : "forward", "targetGroupArn" : self.elb_target_group.ref }],
            load_balancer_arn=self.elastic_load_balancer.ref,
            port=80,
            protocol='HTTP'
        )
        
        # # Aurora MySQL Databases        
        self.db_subnet_group = rds.CfnDBSubnetGroup(self,
            id='DB Subnet Group',
            db_subnet_group_description='DB Subnet Group',
            subnet_ids=[
                self.private_subnet1.ref,
                self.private_subnet2.ref
            ],
            db_subnet_group_name='db-subnet-group',
            tags=[{"key":"Name", "value":"DB SSubnet Group"}]
        )

        self.db_cluster = rds.CfnDBCluster(self,
            id='DB Cluster',
            engine="aurora",
            availability_zones=[
                cdk.Fn.select(0, cdk.Fn.get_azs()),
                cdk.Fn.select(1, cdk.Fn.get_azs())
            ],
            database_name='PRD_DB',
            db_subnet_group_name=self.db_subnet_group.db_subnet_group_name,
            engine_mode="provisioned",
            master_username='administrator',
            master_user_password='Password123!',
            vpc_security_group_ids=[self.db_security_group.ref],
            tags=[{"key":"Name", "value":"DB Cluster"}]
        )
        self.db_cluster.add_depends_on(self.db_subnet_group)

        self.db1 = rds.CfnDBInstance(self,
            id='DB Instance 1',
            engine="aurora",
            db_instance_class="db.t3.small",
            db_cluster_identifier=self.db_cluster.ref,
            db_subnet_group_name=self.db_subnet_group.db_subnet_group_name,
            tags=[{"key":"Name", "value":"DB Instance 1"}]
        )
        self.db1.add_depends_on(self.db_subnet_group)

        self.db2 = rds.CfnDBInstance(self,
            id='DB Instance 2',
            engine="aurora",
            db_instance_class="db.t3.small",
            db_cluster_identifier=self.db_cluster.ref,
            db_subnet_group_name=self.db_subnet_group.db_subnet_group_name,
            tags=[{"key":"Name", "value":"DB Instance 2"}]
        )
        self.db2.add_depends_on(self.db_subnet_group)

        # EC2 Launch Template
        self.ec2_launch_template = ec2.CfnLaunchTemplate(self,
            id='EC2 Launch Template',
            launch_template_name='app-web-launch-template',
            launch_template_data=ec2.CfnLaunchTemplate.LaunchTemplateDataProperty(
                    image_id='ami-03b9ff2958cc4820b',
                    instance_type='t2.medium',
                    security_group_ids=[self.ec2_security_group.ref],
                    iam_instance_profile=ec2.CfnLaunchTemplate.IamInstanceProfileProperty(
                        name='EC2SSM'
                    )
                    )
        )

        # EC2 Auto-Scaling Group
        self.ec2_asg = asg.CfnAutoScalingGroup(self,
            id='auto-scaling group',
            max_size='20',
            min_size='2',
            auto_scaling_group_name='asg',
            availability_zones=[
                cdk.Fn.select(0, cdk.Fn.get_azs()),
                cdk.Fn.select(1, cdk.Fn.get_azs())
            ],
            capacity_rebalance=True,
            cooldown='60',
            desired_capacity='2',
            health_check_grace_period=60,
            health_check_type='EC2',
            launch_template=asg.CfnAutoScalingGroup.LaunchTemplateSpecificationProperty(
                version='8',
                launch_template_id=self.ec2_launch_template.ref,
            ),
            target_group_arns=[
                self.elb_target_group.ref
            ],
            vpc_zone_identifier=[
                self.public_subnet1.ref,
                self.public_subnet2.ref,
            ],
            tags=[asg.CfnAutoScalingGroup.TagPropertyProperty(
                key='1',
                propagate_at_launch=False,
                value='0'
            )]
        )
        self.ec2_asg.add_depends_on(self.db_cluster)
        self.ec2_asg.add_depends_on(self.db1)
        self.ec2_asg.add_depends_on(self.db2)

        # Cloudwatch Metric - CPU Utilization
        self.cwm_cpu = cw.CfnAlarm(self,
            id='cw-cpu-alarm',
            metric_name='CPUUtilization',
            comparison_operator='GreaterThanOrEqualToThreshold',
            actions_enabled=True,
            alarm_name='CPU Utilization',
            threshold=50,
            evaluation_periods=1,
            statistic='Average',
            period=30,
            unit='Percent',
            namespace='CPUUtilization'
        )

        # Scaling Policy
        self.scaling_policy = asg.CfnScalingPolicy(self,
            id='scaling-policy',
            auto_scaling_group_name=self.ec2_asg.ref,
            policy_type='TargetTrackingScaling',
            estimated_instance_warmup=10,
            target_tracking_configuration=asg.CfnScalingPolicy.TargetTrackingConfigurationProperty(
                target_value=50,
                predefined_metric_specification=asg.CfnScalingPolicy.PredefinedMetricSpecificationProperty(
                    predefined_metric_type='ASGAverageCPUUtilization'
                )
            )

        )
