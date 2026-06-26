#!/bin/bash

# Initialize variables to default values
# Initialize variables to default values
DRYRUN=false
VERBOSE=false
SERVICE=""
SOURCE_PATH=""
LDAP=""
REGION="us-central1"
NETWORK=""
MEMORY="512Mi"
SKIP_BUILD=false
SKIP_DEPLOY=false
PROJECT=$(gcloud config get project)

# Function for displaying help/usage (optional but good practice)
usage() {
  echo "Usage: $0 [options]"
  echo ""
  echo "Options:"
  echo "  --service-name <name>   Name of the service"
  echo "  --source <path>         Path to the source code"
  echo "  --user <ldap>           LDAP/user identifier"
  echo "  --region <region>       Cloud Run region (default: europe-west4)"
  echo "  --network <network>     Network to use"
  echo "  --memory <memory>       Memory allocation for Cloud Run (default: 512Mi)"
  echo "  --skip-build            Skip the build step (sets SKIP_BUILD to true)"
  echo "  --skip-deploy           Skip the deploy step (sets SKIP_DEPLOY to true)"
  echo "  --dry-run               Enable dry run mode"
  echo "  --verbose               Enable verbose output"
  echo "  --help                  Display this help message"
  exit 1
}

# Parse command-line arguments
while (( "$#" )); do
  case "$1" in
    --dry-run)
      DRYRUN=true
      shift # consume --dry-run
      ;;
    --verbose)
      VERBOSE=true
      shift # consume --verbose
      ;;
    --skip-build) # New flag
      SKIP_BUILD=true
      shift 
      ;;
    --skip-deploy) # New flag
      SKIP_DEPLOY=true
      shift 
      ;;
    --service-name)
      if [ -n "$2" ] && [[ "$2" != --* ]]; then
        SERVICE="$2"
        shift 2 # consume --service-name and its value
      else
        echo "Error: Argument for $1 is missing or looks like another option." >&2
        usage
      fi
      ;;
    --source)
      if [ -n "$2" ] && [[ "$2" != --* ]]; then
        SOURCE_PATH="$2"
        shift 2
      else
        echo "Error: Argument for $1 is missing or looks like another option." >&2
        usage
      fi
      ;;
    --user)
      if [ -n "$2" ] && [[ "$2" != --* ]]; then
        LDAP="$2"
        shift 2
      else
        echo "Error: Argument for $1 is missing or looks like another option." >&2
        usage
      fi
      ;;
    --region)
      if [ -n "$2" ] && [[ "$2" != --* ]]; then
        REGION="$2"
        shift 2
      else
        echo "Error: Argument for $1 is missing or looks like another option." >&2
        usage
      fi
      ;;
    --network)
      if [ -n "$2" ] && [[ "$2" != --* ]]; then
        NETWORK="$2"
        shift 2
      else
        echo "Error: Argument for $1 is missing or looks like another option." >&2
        usage
      fi
      ;;
    --memory)
      if [ -n "$2" ] && [[ "$2" != --* ]]; then
        MEMORY="$2"
        shift 2
      else
        echo "Error: Argument for $1 is missing or looks like another option." >&2
        usage
      fi
      ;;
    # Optional: Support for --option=value format
    --service-name=*)
      SERVICE="${1#*=}" # Extract value after =
      shift
      ;;
    --source=*)
      SOURCE_PATH="${1#*=}"
      shift
      ;;
    --user=*)
      LDAP="${1#*=}"
      shift
      ;;
    --region=*)
      REGION="${1#*=}"
      shift
      ;;
    --network=*)
      NETWORK="${1#*=}"
      shift
      ;;
    --memory=*)
      MEMORY="${1#*=}"
      shift
      ;;
    --help)
      usage
      ;;
    -*) # Handles unknown options starting with a single hyphen (if any) or double hyphen
      echo "Invalid option: $1" >&2
      usage
      ;;
    *) # Handles non-option arguments if you expect any (not typical for this script)
       # If you don't expect any positional arguments beyond options:
      echo "Error: Unknown argument $1" >&2
      usage
      ;;
  esac
done

if [[ -z "${SERVICE}" ]]; then
  echo "--service_name <service_name> must be specified."
  exit 1
fi

if [[ -z "${LDAP}" ]]; then
  echo "--user <your_ldap> must be specified."
  exit 1
fi

if [[ -n "${NETWORK}" ]]; then
  OTHER_OPTIONS="--network=${NETWORK}"
fi

set -e

function run() {
  cmd=${*}
  if [[ ${DRYRUN} == "true" || ${VERBOSE} == "true" ]]; then
    echo "$ $cmd"
  fi

  if [[ ${DRYRUN} == "true" ]]; then
    echo "dryrun: skipping..."
  else
    eval "$cmd"
  fi
  echo
}

run gcloud services enable iap.googleapis.com
run gcloud services enable compute.googleapis.com
run gcloud services enable cloudresourcemanager.googleapis.com
run gcloud services enable artifactregistry.googleapis.com
run gcloud services enable cloudbuild.googleapis.com
run gcloud services enable run.googleapis.com
run gcloud beta services identity create --service=iap.googleapis.com --project=${PROJECT}
OAUTH_BRAND=$(gcloud iap oauth-brands list --format='value(name)')
if [[ -z ${OAUTH_BRAND} ]]; then
  run gcloud iap oauth-brands create --application_title=${SERVICE} --support_email=admin@${LDAP}.altostrat.com
fi

PROJECT_NUMBER=$(gcloud projects describe ${PROJECT} --format="value(project_number)")
COMPUTE_SERVICE_ACCOUNT=${PROJECT_NUMBER}-compute@developer.gserviceaccount.com
if [[ -z $(gcloud projects get-iam-policy ${PROJECT} --filter="bindings.role:'roles/storage.objectAdmin' AND bindings.members:${COMPUTE_SERVICE_ACCOUNT}") ]]; then
  run gcloud projects add-iam-policy-binding ${PROJECT} --member=serviceAccount:${COMPUTE_SERVICE_ACCOUNT} --role=roles/storage.objectAdmin
fi
if [[ -z $(gcloud projects get-iam-policy ${PROJECT} --filter="bindings.role:'roles/artifactregistry.admin' AND bindings.members:${COMPUTE_SERVICE_ACCOUNT}") ]]; then
  run gcloud projects add-iam-policy-binding ${PROJECT} --member=serviceAccount:${COMPUTE_SERVICE_ACCOUNT} --role=roles/artifactregistry.admin
fi

#---
## Deploying Service
#---

echo "# Deploying service ${SERVICE}..."
if [[ ${SKIP_BUILD} == "true" && ${SKIP_DEPLOY} == "true" ]]; then
  echo "Both build and deploy steps are skipped."
elif [[ ${SKIP_BUILD} == "true" ]]; then
  echo "Skipping build step. Deploying existing image."
  run gcloud run deploy ${SERVICE} --region=${REGION} --no-allow-unauthenticated --ingress=internal-and-cloud-load-balancing --service-account=${COMPUTE_SERVICE_ACCOUNT} --memory=${MEMORY} ${OTHER_OPTIONS}
elif [[ ${SKIP_DEPLOY} == "true" ]]; then
  echo "Skipping deploy step. Only building the image."
  run gcloud run deploy ${SERVICE} --source=$SOURCE_PATH --region=${REGION} --no-allow-unauthenticated --ingress=internal-and-cloud-load-balancing --service-account=${COMPUTE_SERVICE_ACCOUNT} --memory=${MEMORY} ${OTHER_OPTIONS} --dry-run --allow-unauthenticated # --dry-run and --allow-unauthenticated are used to force build without actual deployment
else
  run gcloud run deploy ${SERVICE} --source=$SOURCE_PATH --region=${REGION} --no-allow-unauthenticated --ingress=internal-and-cloud-load-balancing --service-account=${COMPUTE_SERVICE_ACCOUNT} --memory=${MEMORY} ${OTHER_OPTIONS}
fi


IAP_SERVICE_ACCOUNT=serviceAccount:service-${PROJECT_NUMBER}@gcp-sa-iap.iam.gserviceaccount.com
if [[ -z $(gcloud run services get-iam-policy ${SERVICE} --region=${REGION} --format="value(bindings.members)" --filter="bindings.role:'roles/run.invoker' AND bindings.members:${IAP_SERVICE_ACCOUNT}") ]]; then
  echo "# Adding the IAP service account to the cloud run service..." 
  run gcloud run services add-iam-policy-binding ${SERVICE} --member=${IAP_SERVICE_ACCOUNT} --role="roles/run.invoker" --region=${REGION}
fi

IAP_ENABLED=$(gcloud compute backend-services list --format='value(iap.enabled)' --filter=name=${SERVICE}-backends)
if [[ -z ${IAP_ENABLED} ]]; then
  echo "# Creating a backend service ${SERVICE}-backends..."
  run gcloud compute backend-services create ${SERVICE}-backends --global --no-enable-cdn --protocol=HTTPS --port-name=http  --load-balancing-scheme=EXTERNAL_MANAGED
  run gcloud iap web add-iam-policy-binding --resource-type=backend-services --service=${SERVICE}-backends --member="user:admin@${LDAP}.altostrat.com" --role="roles/iap.httpsResourceAccessor"

  echo "# Enabling IAP for ${SERVICE}-backends..."
  run gcloud compute backend-services update ${SERVICE}-backends --global --iap=enabled
fi

SUBDOMAIN=${SERVICE}
LOAD_BALANCER=${SUBDOMAIN}-lb
SSL_CERTIFICATE=${SUBDOMAIN}-ssl-cert

if [[ -n $(gcloud compute url-maps list --global --format="value(name)" --filter=name:${LOAD_BALANCER}) ]]; then
  echo "# Found the existing load balancer ${LOAD_BALANCER}, exiting..."
  exit 0
fi

read -p "Add a new subdomain ${SUBDOMAIN}.${LDAP}.demo.altostrat.com and map it to ${SERVICE}? (y/n)" -r
echo
if [[ ! "$REPLY" =~ ^[Yy]$ ]]; then
  exit 0
fi

DNS_PROJECT=${PROJECT}
read -e -p "Enter DNS project [${DNS_PROJECT}]: " ANSWER
if [[ -n ${ANSWER} ]]; then
  DNS_PROJECT=${ANSWER}
fi

DNS_ZONE=$(gcloud dns managed-zones list --project=${DNS_PROJECT} --format="value(name)" --limit=1)
read -p "Enter DNS zone [${DNS_ZONE}]: " ANSWER
if [[ -n ${ANSWER} ]]; then
  DNS_ZONE=${ANSWER}
fi

echo "# Creating load balancer and ssl certificate for ${SUBDOMAIN}.${LDAP}.demo.altostrat.com..."
run gcloud compute url-maps create ${LOAD_BALANCER} --global --default-service=${SERVICE}-backends
run gcloud compute ssl-certificates create ${SSL_CERTIFICATE} --domains=${SUBDOMAIN}.${LDAP}.demo.altostrat.com --global
run gcloud compute target-https-proxies create ${LOAD_BALANCER}-target-proxy --global --url-map=${LOAD_BALANCER} --ssl-certificates=${SSL_CERTIFICATE}
run gcloud compute forwarding-rules create ${SUBDOMAIN}-frontend --load-balancing-scheme=EXTERNAL_MANAGED --network-tier=PREMIUM --global --target-https-proxy=${LOAD_BALANCER}-target-proxy --ports=443
run gcloud compute network-endpoint-groups create ${SERVICE}-backends-serverless --network-endpoint-type=serverless --region=${REGION} --cloud-run-service=${SERVICE}
run gcloud compute backend-services add-backend ${SERVICE}-backends --network-endpoint-group=${SERVICE}-backends-serverless --network-endpoint-group-region=${REGION} --global

if [[ -z $(gcloud dns record-sets list --zone=${DNS_ZONE} --project=${DNS_PROJECT} --format="value(name)" --filter=name:${SUBDOMAIN}.${LDAP}.demo.altostrat.com) ]]; then
  echo "# Adding a DNS record for ${SUBDOMAIN}.${LDAP}.demo.altostrat.com. IP address: ${LB_IP_ADDRESS}..."
  LB_IP_ADDRESS=$(gcloud compute forwarding-rules describe ${SUBDOMAIN}-frontend --global --format="value(IPAddress)")
  run gcloud dns --project=${DNS_PROJECT} record-sets create ${SUBDOMAIN}.${LDAP}.demo.altostrat.com. --zone=${DNS_ZONE} --type="A" --ttl="300" --rrdatas="${LB_IP_ADDRESS}"
fi

echo "# Done!"
echo "# NOTE: Adding the subdomain in DNS and provisioning SSL certificates may take up to 24 hours. (Typically much faster). You can check the status by running `gcloud compute ssl-certificates list`"

set +e