#!/usr/bin/env sh
"\"",`$(echo --% ' |out-null)" >$null;function :{};function dv{<#${/*'>/dev/null )` 2>/dev/null;dv() { #>
echo "1.42.1"; : --% ' |out-null <#'; }; version="$(dv)"; deno="$HOME/.deno/$version/bin/deno"; if [ -x "$deno" ]; then  exec "$deno" run -q -A --no-lock "$0" "$@";  elif [ -f "$deno" ]; then  chmod +x "$deno" && exec "$deno" run -q -A --no-lock "$0" "$@";  fi; bin_dir="$HOME/.deno/$version/bin"; exe="$bin_dir/deno"; has () { command -v "$1" >/dev/null; } ;  if ! has unzip; then if ! has apt-get; then  has brew && brew install unzip; else  if [ "$(whoami)" = "root" ]; then  apt-get install unzip -y; elif has sudo; then  echo "Can I install unzip for you? (its required for this command to work) ";read ANSWER;echo;  if [ "$ANSWER" = "y" ] || [ "$ANSWER" = "yes" ] || [ "$ANSWER" = "Y" ]; then  sudo apt-get install unzip -y; fi; elif has doas; then  echo "Can I install unzip for you? (its required for this command to work) ";read ANSWER;echo;  if [ "$ANSWER" = "y" ] || [ "$ANSWER" = "yes" ] || [ "$ANSWER" = "Y" ]; then  doas apt-get install unzip -y; fi; fi;  fi;  fi;  if ! has unzip; then  echo ""; echo "So I couldn't find an 'unzip' command"; echo "And I tried to auto install it, but it seems that failed"; echo "(This script needs unzip and either curl or wget)"; echo "Please install the unzip command manually then re-run this script"; exit 1;  fi;  repo="denoland/deno"; if [ "$OS" = "Windows_NT" ]; then target="x86_64-pc-windows-msvc"; else :;  case $(uname -sm) in "Darwin x86_64") target="x86_64-apple-darwin" ;; "Darwin arm64") target="aarch64-apple-darwin" ;; "Linux aarch64") repo="LukeChannings/deno-arm64" target="linux-arm64" ;; "Linux armhf") echo "deno sadly doesn't support 32-bit ARM. Please check your hardware and possibly install a 64-bit operating system." exit 1 ;; *) target="x86_64-unknown-linux-gnu" ;; esac; fi; deno_uri="https://github.com/$repo/releases/download/v$version/deno-$target.zip"; exe="$bin_dir/deno"; if [ ! -d "$bin_dir" ]; then mkdir -p "$bin_dir"; fi;  if ! curl --fail --location --progress-bar --output "$exe.zip" "$deno_uri"; then if ! wget --output-document="$exe.zip" "$deno_uri"; then echo "Howdy! I looked for the 'curl' and for 'wget' commands but I didn't see either of them. Please install one of them, otherwise I have no way to install the missing deno version needed to run this code"; exit 1; fi; fi; unzip -d "$bin_dir" -o "$exe.zip"; chmod +x "$exe"; rm "$exe.zip"; exec "$deno" run -q -A --no-lock "$0" "$@"; #>}; $DenoInstall = "${HOME}/.deno/$(dv)"; $BinDir = "$DenoInstall/bin"; $DenoExe = "$BinDir/deno.exe"; if (-not(Test-Path -Path "$DenoExe" -PathType Leaf)) { $DenoZip = "$BinDir/deno.zip"; $DenoUri = "https://github.com/denoland/deno/releases/download/v$(dv)/deno-x86_64-pc-windows-msvc.zip";  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12;  if (!(Test-Path $BinDir)) { New-Item $BinDir -ItemType Directory | Out-Null; };  Function Test-CommandExists { Param ($command); $oldPreference = $ErrorActionPreference; $ErrorActionPreference = "stop"; try {if(Get-Command "$command"){RETURN $true}} Catch {Write-Host "$command does not exist"; RETURN $false}; Finally {$ErrorActionPreference=$oldPreference}; };  if (Test-CommandExists curl) { curl -Lo $DenoZip $DenoUri; } else { curl.exe -Lo $DenoZip $DenoUri; };  if (Test-CommandExists curl) { tar xf $DenoZip -C $BinDir; } else { tar -Lo $DenoZip $DenoUri; };  Remove-Item $DenoZip;  $User = [EnvironmentVariableTarget]::User; $Path = [Environment]::GetEnvironmentVariable('Path', $User); if (!(";$Path;".ToLower() -like "*;$BinDir;*".ToLower())) { [Environment]::SetEnvironmentVariable('Path', "$Path;$BinDir", $User); $Env:Path += ";$BinDir"; } }; & "$DenoExe" run -q -A --no-lock "$PSCommandPath" @args; Exit $LastExitCode; <# 
# */0}`;
import { FileSystem } from "https://deno.land/x/quickr@0.6.44/main/file_system.js"
import { Console, bold, lightRed, yellow } from "https://deno.land/x/quickr@0.6.44/main/console.js"
import { run, Timeout, Env, Cwd, Stdin, Stdout, Stderr, Out, Overwrite, AppendTo, throwIfFails, returnAsString, zipInto, mergeInto } from "https://deno.land/x/quickr@0.6.44/main/run.js"

const argsWereGiven = Deno.args.length > 0

const testsFolder = `${FileSystem.thisFolder}/../tests`
const logsFolder = `${FileSystem.thisFolder}/../logs`

await FileSystem.ensureIsFolder(testsFolder)
await FileSystem.ensureIsFolder(logsFolder)
Deno.chdir(logsFolder)

console.log("\nRunning tests")
for (const each of await FileSystem.recursivelyListItemsIn(testsFolder)) {
    if (each.isFile) {
        // if one is mentioned, only run mentioned ones
        if (argsWereGiven && !(Deno.args.includes(each.name) || Deno.args.includes(each.basename))) {
            continue
        }
        const relativePart = FileSystem.makeRelativePath({ from: testsFolder, to: each.path })
        const logPath = `${logsFolder}/${relativePart}.log`
        const logRelativeToProject = FileSystem.makeRelativePath({ from: `${testsFolder}/..`, to: logPath })
        let pathOutsideOfProject = FileSystem.normalize(`${FileSystem.thisFolder}/../`)
        if (pathOutsideOfProject.endsWith("/")) {
            pathOutsideOfProject = pathOutsideOfProject.slice(0, -1)
        }
        await FileSystem.clearAPathFor(logPath, {overwrite: true})
        try {
            if (each.path.endsWith(".yaml") || each.path.endsWith(".yml") || each.path.endsWith(".json")) {
                continue
            }
            await FileSystem.addPermissions({
                path: each.path,
                permissions: {
                    owner: {canExecute: true},
                }
            })
            if (each.path.endsWith(".js")) {
                var { success } = await run("deno", "run", "-A", each.path, Out(Overwrite(logPath)), Env({NO_COLOR:"true"}))
            } else if (each.path.endsWith(".py")) {
                var { success } = await run("python", each.path, Out(Overwrite(logPath)), Env({NO_COLOR:"true"}))
            } else {
                var { success } = await run(each.path, Out(Overwrite(logPath)), Env({NO_COLOR:"true"}))
            }
            if (success) {
                FileSystem.read(logPath).then(async (data) => {
                    await FileSystem.write({
                        data: data.replaceAll(pathOutsideOfProject, "$PROJECT_ROOT"),
                        path: logPath,
                    })
                }).catch(console.error)
            }
        } catch (error) {
            console.log(bold.lightRed`    Error with test: `.yellow`${relativePart}:`.blue` ${error.message}`)
            continue
        }
        if (!success) {
            console.log(bold.lightRed`    Error with test: `.yellow`${relativePart}:`.blue` ${logRelativeToProject}`)
        } else {
            console.log(bold.lightGreen`    Passed: `.yellow`${relativePart}:`.blue` ${logRelativeToProject}`)
        }
    }
}
// (this comment is part of deno-guillotine, dont remove) #>