# Stage 1: Build the .NET API
FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build-env
WORKDIR /source

# Copy the entire monorepo into the build environment
COPY . .

# Navigate into the actual folder where api.csproj lives
WORKDIR /source/api
RUN dotnet restore
RUN dotnet publish -c Release -o /app/out

# Stage 2: Create the lean runtime environment
FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app

# Copy the compiled API from the build stage
COPY --from=build-env /app/out .

# Copy your actual local database file into the app directory
COPY data_pipeline/lastfm_data.db .

# Tell Docker which port we want to use
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080

# Start the API (matching your api.csproj output)
ENTRYPOINT ["dotnet", "api.dll"]